#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
import json
import time
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tempfile
import urllib.request
from PyPDF2 import PdfReader
from openai import OpenAI

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))
from constants import (
    CLIMATE_REPORT_RESOURCES,
    REQUIRED_REPORTS,
    ACT_COMPANIES,
    EDUCATION_RESOURCES,
    MASSACHUSETTS_CLIMATE_RESOURCES,
    mark_company_as_indexed,
    get_unindexed_companies,
    save_company_index_status
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('url_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize base headers for Supabase requests
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Default system user ID
SYSTEM_USER_ID = "system"

# Try to import constants, but provide a fallback if it fails
try:
    from constants import (
        CLIMATE_REPORT_RESOURCES,
        REQUIRED_REPORTS,
        ACT_COMPANIES,
    )
except ImportError:
    logging.warning("Could not import constants, using fallbacks")
    CLIMATE_REPORT_RESOURCES = []
    REQUIRED_REPORTS = []
    # Define a fallback for ACT_COMPANIES
    ACT_COMPANIES = [
        {"name": "Solaris Energy", "sector": "Solar", "location": "Boston", "website": "https://solarisenergy.com"},
        {"name": "WindTech Solutions", "sector": "Wind", "location": "Worcester", "website": "https://windtechsolutions.com"},
        {"name": "EcoGrid Systems", "sector": "Energy Efficiency", "location": "Cambridge", "website": "https://ecogridsystems.com"},
        {"name": "GreenBuild Contractors", "sector": "Green Building", "location": "Springfield", "website": "https://greenbuildcontractors.com"},
        {"name": "BatteryStore Inc.", "sector": "Battery Storage", "location": "Boston", "website": "https://batterystoreinc.com"}
    ]

# Function to get ACT companies from Supabase if available
async def get_act_companies_from_db():
    """Retrieve ACT companies from the database instead of constants"""
    try:
        from supabase import create_client, Client
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url=supabase_url, supabase_key=supabase_key)
            response = supabase.table("companies").select("*").execute()
            if response and hasattr(response, 'data') and response.data:
                logging.info(f"Retrieved {len(response.data)} companies from database")
                return response.data
        
        logging.warning("No companies found in database, using fallback")
        return ACT_COMPANIES
    except Exception as e:
        logging.error(f"Error retrieving companies from database: {e}")
        return ACT_COMPANIES

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0
        self.lock = asyncio.Lock()
    
    async def wait(self):
        """Wait if necessary to comply with rate limits."""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call_time
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self.last_call_time = time.time()

class URLIngester:
    """Climate Economy Ecosystem URL ingester."""
    
    def __init__(self):
        """Initialize the URL ingester."""
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize rate limiter for API calls
        self.supabase_rate_limiter = RateLimiter(2.0)  # 2 calls per second
        self.url_rate_limiter = RateLimiter(0.5)  # 1 call per 2 seconds to be respectful
        
        # Configuration for processing
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.browser_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        try:
            # Use OpenAI's embedding model
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"  # 1536 dimensions
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding with OpenAI: {str(e)}")
            return None
    
    def smart_chunker(self, text: str) -> List[str]:
        """Split text into chunks intelligently, preserving context."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        # Split text into sentences
        segments = re.split(r'([.!?]\s+|\n{2,})', text)
        
        for i in range(0, len(segments), 2):
            segment = segments[i]
            # Add the punctuation/newline back if it exists
            if i + 1 < len(segments):
                segment += segments[i + 1]
                
            # If adding this segment would exceed chunk size, start new chunk
            if current_length + len(segment) > self.chunk_size and current_chunk:
                chunks.append(''.join(current_chunk).strip())
                
                # Start new chunk with overlap from previous
                overlap_start = max(0, len(''.join(current_chunk)) - self.chunk_overlap)
                current_chunk = [''.join(current_chunk)[overlap_start:]]
                current_length = len(current_chunk[0])
            
            current_chunk.append(segment)
            current_length += len(segment)
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(''.join(current_chunk).strip())
        
        # Limit chunks for processing sanity
        MAX_CHUNKS = 20  # Limit for URL content
        if len(chunks) > MAX_CHUNKS:
            logger.warning(f"Too many chunks ({len(chunks)}), limiting to {MAX_CHUNKS}")
            chunks = chunks[:MAX_CHUNKS]
            
        return chunks
    
    async def memory_exists(self, url: str, chunk_index: Optional[int] = None) -> bool:
        """Check if a memory with the given URL and chunk index already exists."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Build the query to search in metadata
            metadata_filter = f"metadata->>'url'=eq.{requests.utils.quote(url)}"
            if chunk_index is not None:
                metadata_filter += f"&metadata->>'chunk_index'=eq.{chunk_index}"
            
            query_url = f"{SUPABASE_URL}/rest/v1/climate_memories?select=id&{metadata_filter}"
            
            # Make request
            response = requests.get(
                query_url,
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200:
                data = response.json()
                return len(data) > 0
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking if memory exists: {str(e)}")
            return False
    
    async def store_memory(self, content: str, user_id: str, metadata: Dict) -> bool:
        """Store a memory in the climate_memories table with embedding."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Skip if content is too short
            if not content or len(content.strip()) < 50:
                logger.warning(f"Content too short, skipping: {metadata.get('url', 'unknown')}")
                return False
            
            # Check if memory already exists
            if 'url' in metadata:
                chunk_index = metadata.get('chunk_index')
                if await self.memory_exists(metadata['url'], chunk_index):
                    logger.info(f"Memory from {metadata['url']} already exists, skipping")
                    return True  # Consider it a success
            
            # Create memory data
            memory_data = {
                'content': content,
                'user_id': user_id,  # Required field
                'metadata': metadata
            }
            
            # Add embedding if available
            embedding = await self.get_embedding(content)
            if embedding:
                memory_data['embedding'] = embedding
            
            # Insert into Supabase
            await self.supabase_rate_limiter.wait()
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/climate_memories",
                headers=SUPABASE_HEADERS,
                json=memory_data
            )
            
            if response.status_code == 201:
                logger.info(f"Successfully inserted memory from {metadata.get('url', 'unknown')}")
                return True
            else:
                logger.error(f"Failed to insert memory: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return False
    
    async def download_and_process_pdf(self, url: str) -> Optional[Dict]:
        """Download a PDF from a URL and process it."""
        try:
            logger.info(f"Downloading PDF from URL: {url}")
            
            # Wait for rate limiting
            await self.url_rate_limiter.wait()
            
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Download the PDF
                urllib.request.urlretrieve(url, temp_path)
                
                # Process the PDF
                reader = PdfReader(temp_path)
                content = ""
                metadata = {}
                
                # Extract metadata if available
                if reader.metadata:
                    metadata = {k.lower().replace('/', '_'): v for k, v in reader.metadata.items() if v}
                
                # Extract text from all pages
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
                
                logger.info(f"Successfully processed PDF from {url} ({len(reader.pages)} pages)")
                
                # Clean up the temporary file
                os.unlink(temp_path)
                
                # Return the result
                return {
                    'content': content,
                    'metadata': {
                        **metadata,
                        'file_type': 'pdf',
                        'url': url,
                        'file_name': url.split('/')[-1],
                        'num_pages': len(reader.pages),
                        'indexed_at': datetime.now(timezone.utc).isoformat()
                    }
                }
        
        except Exception as e:
            logger.error(f"Error downloading and processing PDF from {url}: {str(e)}")
            return None
    
    async def process_webpage(self, url: str) -> Optional[Dict]:
        """Process a webpage."""
        try:
            logger.info(f"Processing webpage: {url}")
            
            # Wait for rate limiting
            await self.url_rate_limiter.wait()
            
            # Fetch the webpage
            response = requests.get(url, headers=self.browser_headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract the domain for the source
            domain = urlparse(url).netloc
            
            # Extract the title
            title = soup.title.string if soup.title else url.split('/')[-1]
            
            # Extract all text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'\s{2,}', ' ', text)
            
            logger.info(f"Successfully processed webpage: {url}")
            
            return {
                'content': text,
                'metadata': {
                    'file_type': 'webpage',
                    'url': url,
                    'title': title,
                    'domain': domain,
                    'indexed_at': datetime.now(timezone.utc).isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error processing webpage {url}: {str(e)}")
            return None
    
    async def process_url(self, url: str, source_type: str = 'report', organization: str = None) -> bool:
        """Process a URL (either webpage or PDF)."""
        try:
            # Check if URL already processed
            if await self.memory_exists(url):
                logger.info(f"URL {url} already processed, skipping")
                return True
                
            # Check if URL is a PDF
            if url.lower().endswith('.pdf'):
                # Process PDF
                result = await self.download_and_process_pdf(url)
            else:
                # Process webpage
                result = await self.process_webpage(url)
            
            if not result:
                logger.error(f"Failed to process URL: {url}")
                return False
            
            # Add additional metadata
            result['metadata']['source_type'] = source_type
            if organization:
                result['metadata']['organization'] = organization
            
            # For long content, split into chunks
            content = result['content']
            if len(content) > self.chunk_size:
                chunks = self.smart_chunker(content)
                logger.info(f"Split content into {len(chunks)} chunks")
                
                # Store each chunk as a separate memory
                success_count = 0
                for i, chunk in enumerate(chunks):
                    # Add chunk metadata
                    chunk_metadata = {
                        **result['metadata'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                    
                    # Store the chunk
                    if await self.store_memory(chunk, SYSTEM_USER_ID, chunk_metadata):
                        success_count += 1
                
                logger.info(f"Successfully stored {success_count}/{len(chunks)} chunks from {url}")
                return success_count > 0
            else:
                # Store single document
                if await self.store_memory(content, SYSTEM_USER_ID, result['metadata']):
                    logger.info(f"Successfully stored content from {url}")
                    return True
                else:
                    logger.error(f"Failed to store content from {url}")
                    return False
                
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return False
    
    async def process_climate_reports(self) -> int:
        """Process all climate report URLs."""
        logger.info("Processing climate report URLs...")
        success_count = 0
        
        for report_url in CLIMATE_REPORT_RESOURCES:
            # Skip local files
            if not report_url.startswith('http'):
                continue
                
            logger.info(f"Processing climate report: {report_url}")
            if await self.process_url(report_url, 'climate_report'):
                success_count += 1
                
        logger.info(f"Successfully processed {success_count} climate report URLs")
        return success_count
    
    async def process_company_resources(self, company_name: str = None) -> int:
        """Process resources for a specific company or all companies."""
        success_count = 0
        companies_to_process = []
        
        if company_name:
            # Find the specified company
            for company in ACT_COMPANIES:
                if company['name'] == company_name:
                    companies_to_process.append(company)
                    break
        else:
            # Process unindexed companies
            companies_to_process = get_unindexed_companies()
        
        if not companies_to_process:
            logger.info(f"No companies to process")
            return 0
        
        logger.info(f"Processing resources for {len(companies_to_process)} companies")
        
        for company in companies_to_process:
            company_name = company['name']
            company_resources = company.get('resources', [])
            company_sector = company.get('sector', '')
            company_url_count = 0
            
            logger.info(f"Processing resources for company: {company_name}")
            
            # Process each resource URL
            for resource_url in company_resources:
                # Skip non-HTTP URLs
                if not resource_url.startswith('http'):
                    continue
                
                logger.info(f"Processing resource: {resource_url}")
                
                # Process the URL with company metadata
                if await self.process_url(
                    resource_url, 
                    'company_resource', 
                    company_name
                ):
                    company_url_count += 1
                    success_count += 1
                
                # Avoid overwhelming servers
                await asyncio.sleep(1)
            
            logger.info(f"Processed {company_url_count} URLs for {company_name}")
            
            # Mark company as indexed
            if company_url_count > 0:
                mark_company_as_indexed(company_name)
                
            # Save progress after each company
            save_company_index_status()
        
        logger.info(f"Successfully processed {success_count} company resource URLs")
        return success_count
    
    async def process_education_resources(self) -> int:
        """Process education resource URLs."""
        logger.info("Processing education resource URLs...")
        success_count = 0
        
        for resource_url in EDUCATION_RESOURCES:
            # Skip non-HTTP URLs
            if not resource_url.startswith('http'):
                continue
                
            logger.info(f"Processing education resource: {resource_url}")
            if await self.process_url(resource_url, 'education_resource'):
                success_count += 1
                
            # Avoid overwhelming servers
            await asyncio.sleep(1)
                
        logger.info(f"Successfully processed {success_count} education resource URLs")
        return success_count

    async def process_company_data(self) -> int:
        """Directly ingest company information from constants.py."""
        logger.info("Processing company data directly...")
        success_count = 0
        
        for company in ACT_COMPANIES:
            company_name = company.get('name', '')
            company_description = company.get('description', '')
            company_location = company.get('location', '')
            company_sector = company.get('sector', '')
            company_focus_areas = company.get('focus_areas', [])
            company_audience = company.get('audience', [])
            company_skill_sets = company.get('skill_sets', [])
            
            logger.info(f"Processing company data for: {company_name}")
            
            # Construct rich company content with all details
            content = f"Company: {company_name}\n\n"
            content += f"Description: {company_description}\n\n"
            content += f"Location: {company_location}\n\n"
            content += f"Sector: {company_sector}\n\n"
            
            if company_focus_areas:
                content += f"Focus Areas: {', '.join(company_focus_areas)}\n\n"
            
            if company_audience:
                content += f"Target Audience: {', '.join(company_audience)}\n\n"
            
            if company_skill_sets:
                content += f"Skill Sets: {', '.join(company_skill_sets)}\n\n"
            
            # Create metadata
            metadata = {
                'source_type': 'company_data',
                'company_name': company_name,
                'company_sector': company_sector,
                'company_location': company_location,
                'indexed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Store the company data
            if await self.store_memory(content, SYSTEM_USER_ID, metadata):
                success_count += 1
                logger.info(f"Successfully stored company data for: {company_name}")
            else:
                logger.error(f"Failed to store company data for: {company_name}")
            
        logger.info(f"Successfully processed data for {success_count}/{len(ACT_COMPANIES)} companies")
        return success_count

async def main() -> None:
    """Main function to run the URL ingestion process."""
    try:
        logger.info("Starting URL ingestion process...")
        
        # Create ingester
        ingester = URLIngester()
        
        # Process climate report URLs
        await ingester.process_climate_reports()
        
        # Process company resources
        await ingester.process_company_resources()
        
        # Process education resources
        await ingester.process_education_resources()
        
        # Process company data
        await ingester.process_company_data()
        
        logger.info("URL ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during URL ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 