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
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdown
from openai import OpenAI

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data_ingestion.log')
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

# Initialize OpenAI client if needed for embeddings
openai_client = OpenAI()

# Try to import constants, but provide a fallback if it fails
try:
    from constants import (
        CLIMATE_REPORT_RESOURCES,
        REQUIRED_REPORTS,
        ACT_COMPANIES,
    )
except ImportError:
    logger.warning("Could not import constants, using fallbacks")
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

class ClimateDataIngester:
    def __init__(self):
        # Initialize rate limiter for Supabase calls
        self.supabase_rate_limiter = RateLimiter(2.0)  # 2 calls per second
        
        # Configuration for processing
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        try:
            # Use OpenAI's embedding model
            response = openai_client.embeddings.create(
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
        MAX_CHUNKS = 50
        if len(chunks) > MAX_CHUNKS:
            logger.warning(f"Too many chunks ({len(chunks)}), limiting to {MAX_CHUNKS}")
            chunks = chunks[:MAX_CHUNKS]
            
        return chunks
    
    async def memory_exists(self, source: str, chunk_index: Optional[int] = None) -> bool:
        """Check if a memory already exists in the database."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Create a filter for the query
            query_params = {
                'source': source
            }
            
            # Add chunk index to filter if provided
            if chunk_index is not None:
                query_params['chunk_index'] = chunk_index
                
            # Build the query URL
            url = f"{SUPABASE_URL}/rest/v1/climate_memories"
            
            # Add the filter to only match memories with the same source and chunk index
            filter_str = f"metadata->>'source'=eq.{source}"
            if chunk_index is not None:
                filter_str += f"&metadata->>'chunk_index'=eq.{chunk_index}"
                
            response = requests.get(
                f"{url}?select=id&{filter_str}",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200:
                results = response.json()
                return len(results) > 0
                
            return False
            
        except Exception as e:
            logger.warning(f"Error checking if memory exists: {str(e)}")
            # Default to not existing to be safe
            return False
    
    async def store_memory(self, content: str, metadata: Dict = None) -> bool:
        """Store a memory in the climate_memories table with embedding."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Skip if content is too short
            if not content or len(content.strip()) < 50:
                logger.warning(f"Content too short from {metadata.get('source', 'unknown')}, skipping")
                return False
            
            # Check if memory already exists
            if metadata and 'source' in metadata:
                chunk_index = metadata.get('chunk_index')
                if await self.memory_exists(metadata['source'], chunk_index):
                    logger.info(f"Memory from {metadata['source']} already exists, skipping")
                    return True  # Consider it a success
            
            # Create memory data according to the schema
            memory_data = {
                'content': content,
                'metadata': metadata or {},
                'source_type': metadata.get('type', 'document'),
                'url': metadata.get('url', ''),
                'title': metadata.get('title', metadata.get('file_name', '')),
                'chunk_index': metadata.get('chunk_index'),
                'total_chunks': metadata.get('total_chunks'),
                'company': metadata.get('company_name', ''),
                'sector': metadata.get('sector_name', '')
            }
            
            # Add embedding if we have OpenAI API key
            if os.getenv('OPENAI_API_KEY'):
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
                logger.info(f"Successfully inserted memory from {metadata.get('source', 'unknown')}")
                return True
            else:
                logger.error(f"Failed to insert memory: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return False
    
    async def process_pdf(self, file_path: str) -> Dict:
        """Process a PDF file."""
        try:
            reader = PdfReader(file_path)
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
                
            logger.info(f"Successfully processed PDF: {file_path} ({len(reader.pages)} pages)")
            
            return {
                'content': content,
                'metadata': {
                    **metadata,
                    'file_type': 'pdf',
                    'file_name': Path(file_path).name,
                    'num_pages': len(reader.pages),
                    'indexed_at': datetime.now(timezone.utc).isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error processing PDF file {file_path}: {str(e)}")
            return None
    
    async def process_markdown(self, file_path: str) -> Dict:
        """Process a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert markdown to plain text
            html_content = markdown.markdown(md_content)
            # A simple way to strip HTML tags
            plain_text = re.sub(r'<[^>]+>', ' ', html_content)
            
            logger.info(f"Successfully processed markdown: {file_path}")
            
            return {
                'content': plain_text,
                'metadata': {
                    'file_type': 'markdown',
                    'file_name': Path(file_path).name,
                    'indexed_at': datetime.now(timezone.utc).isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error processing markdown file {file_path}: {str(e)}")
            return None
    
    async def process_document(self, file_path: str) -> Optional[Dict]:
        """Process a document based on its file extension."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return await self.process_pdf(str(file_path))
        elif file_path.suffix.lower() == '.md':
            return await self.process_markdown(str(file_path))
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return None
    
    async def process_documents_directory(self, directory: str) -> None:
        """Process all documents in a directory."""
        try:
            docs_dir = Path(directory)
            if not docs_dir.exists():
                logger.warning(f"Directory {directory} does not exist")
                return

            # Find all PDF files only (skip markdown files)
            files_to_process = []
            for file_path in docs_dir.glob('**/*.pdf'):
                if file_path.is_file():
                    files_to_process.append(file_path)
            
            logger.info(f"Found {len(files_to_process)} documents to process")
            
            # Process files sequentially
            for file_path in files_to_process:
                logger.info(f"Processing document: {file_path}")
                
                # Process the document
                result = await self.process_document(str(file_path))
                
                if not result:
                    logger.error(f"Failed to process document: {file_path}")
                    continue
                
                # For long documents, split into chunks
                content = result['content']
                if len(content) > self.chunk_size:
                    chunks = self.smart_chunker(content)
                    logger.info(f"Split document into {len(chunks)} chunks")
                    
                    # Store each chunk as a separate memory
                    success_count = 0
                    for i, chunk in enumerate(chunks):
                        # Add chunk metadata
                        chunk_metadata = {
                            **result['metadata'],
                            'source': str(file_path),
                            'type': 'document',
                            'chunk_index': i,
                            'total_chunks': len(chunks)
                        }
                        
                        # Store the chunk
                        if await self.store_memory(chunk, chunk_metadata):
                            success_count += 1
                    
                    logger.info(f"Successfully stored {success_count}/{len(chunks)} chunks from {file_path}")
                else:
                    # Store single document
                    metadata = {
                        **result['metadata'],
                        'source': str(file_path),
                        'type': 'document'
                    }
                    
                    if await self.store_memory(content, metadata):
                        logger.info(f"Successfully stored document: {file_path}")
                    else:
                        logger.error(f"Failed to store document: {file_path}")
                
        except Exception as e:
            logger.error(f"Error processing documents directory: {str(e)}")
            raise
    
    async def company_exists(self, company_name: str) -> Optional[str]:
        """Check if a company already exists in the database."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # URL encode the name for the query
            encoded_name = requests.utils.quote(company_name)
            
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/companies?select=id&name=eq.{encoded_name}",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200 and response.json():
                company_id = response.json()[0]['id']
                return company_id
            
            return None
                
        except Exception as e:
            logger.error(f"Error checking if company exists: {str(e)}")
            return None
    
    async def insert_company(self, company_data: Dict) -> Optional[str]:
        """Insert a company into the companies table."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Check if company already exists by name
            if 'name' in company_data:
                company_id = await self.company_exists(company_data['name'])
                if company_id:
                    logger.info(f"Company '{company_data['name']}' already exists with ID {company_id}, updating")
                    
                    # Update existing company
                    await self.supabase_rate_limiter.wait()
                    response = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/companies?id=eq.{company_id}",
                        headers=SUPABASE_HEADERS,
                        json=company_data
                    )
                    
                    if response.status_code in [200, 204]:
                        logger.info(f"Successfully updated company: {company_data['name']}")
                        return company_id
                    else:
                        logger.error(f"Failed to update company: {response.status_code} {response.text}")
                        return company_id  # Still return ID since it exists
            
            # Insert new company
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/companies",
                headers=SUPABASE_HEADERS,
                json=company_data
            )
            
            if response.status_code == 201 and response.json():
                company_id = response.json()[0]['id']
                logger.info(f"Successfully inserted company: {company_data.get('name', 'Unknown')}")
                return company_id
            else:
                logger.error(f"Failed to insert company: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error inserting company: {str(e)}")
            return None
    
    async def insert_job_opportunity(self, job_data: Dict) -> bool:
        """Insert a job opportunity into the job_opportunities table."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Insert job opportunity
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/job_opportunities",
                headers=SUPABASE_HEADERS,
                json=job_data
            )
            
            if response.status_code == 201:
                logger.info(f"Successfully inserted job opportunity: {job_data.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"Failed to insert job opportunity: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting job opportunity: {str(e)}")
            return False
    
    async def training_program_exists(self, title: str, provider: str) -> Optional[str]:
        """Check if a training program already exists in the database."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # URL encode the parameters
            encoded_title = requests.utils.quote(title)
            encoded_provider = requests.utils.quote(provider)
            
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/training_programs?select=id&title=eq.{encoded_title}&provider=eq.{encoded_provider}",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200 and response.json():
                program_id = response.json()[0]['id']
                return program_id
            
            return None
                
        except Exception as e:
            logger.error(f"Error checking if training program exists: {str(e)}")
            return None
    
    async def insert_training_program(self, program_data: Dict) -> bool:
        """Insert a training program into the training_programs table."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Check if program already exists by title and provider
            if 'title' in program_data and 'provider' in program_data:
                program_id = await self.training_program_exists(program_data['title'], program_data['provider'])
                
                if program_id:
                    logger.info(f"Training program '{program_data['title']}' already exists, updating")
                    
                    # Update existing program
                    await self.supabase_rate_limiter.wait()
                    response = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/training_programs?id=eq.{program_id}",
                        headers=SUPABASE_HEADERS,
                        json=program_data
                    )
                    
                    if response.status_code in [200, 204]:
                        logger.info(f"Successfully updated training program: {program_data['title']}")
                        return True
                    else:
                        logger.error(f"Failed to update training program: {response.status_code} {response.text}")
                        return False
            
            # Insert new program
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/training_programs",
                headers=SUPABASE_HEADERS,
                json=program_data
            )
            
            if response.status_code == 201:
                logger.info(f"Successfully inserted training program: {program_data.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"Failed to insert training program: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting training program: {str(e)}")
            return False
    
    async def insert_sector(self, sector_data: Dict) -> bool:
        """Insert a sector into the sectors table."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Check if sector already exists by name
            if 'name' in sector_data:
                encoded_name = requests.utils.quote(sector_data['name'])
                response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/sectors?select=id&name=eq.{encoded_name}",
                    headers=SUPABASE_HEADERS
                )
                
                if response.status_code == 200 and response.json():
                    sector_id = response.json()[0]['id']
                    logger.info(f"Sector '{sector_data['name']}' already exists, updating")
                    
                    # Update existing sector
                    await self.supabase_rate_limiter.wait()
                    response = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/sectors?id=eq.{sector_id}",
                        headers=SUPABASE_HEADERS,
                        json=sector_data
                    )
                    
                    if response.status_code in [200, 204]:
                        logger.info(f"Successfully updated sector: {sector_data['name']}")
                        return True
                    else:
                        logger.error(f"Failed to update sector: {response.status_code} {response.text}")
                        return False
            
            # Insert new sector
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/sectors",
                headers=SUPABASE_HEADERS,
                json=sector_data
            )
            
            if response.status_code == 201:
                logger.info(f"Successfully inserted sector: {sector_data.get('name', 'Unknown')}")
                return True
            else:
                logger.error(f"Failed to insert sector: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting sector: {str(e)}")
            return False
    
    async def process_act_companies(self) -> None:
        """Process and insert ACT_COMPANIES data from constants.py."""
        logger.info("Processing ACT_COMPANIES data")
        
        try:
            # Try to get companies from database first
            companies = await self.get_act_companies_from_db()
            if not companies:
                companies = ACT_COMPANIES
            
            success_count = 0
            for company in companies:
                try:
                    # Extract data from company dict
                    company_data = {
                        "name": company.get("name"),
                        "sector": company.get("sector"),
                        "website": company.get("website"),
                        "description": company.get("description", ""),
                        "location": company.get("location", ""),
                        "focus_areas": json.dumps(company.get("focus_areas", [])),
                        "audience": json.dumps(company.get("audience", [])),
                        "skill_sets": json.dumps(company.get("skill_sets", [])),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "is_veteran_friendly": company.get("is_veteran_friendly", False),
                        "is_ej_friendly": company.get("is_ej_friendly", False),
                        "is_gateway_focused": company.get("is_gateway_focused", False),
                    }
                    
                    # Insert into companies table
                    response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/companies",
                        headers=SUPABASE_HEADERS,
                        json=company_data
                    )
                    
                    if response.status_code == 201 and response.json():
                        success_count += 1
                        logger.info(f"Successfully added company: {company.get('name')}")
                    else:
                        logger.warning(f"Failed to add company: {company.get('name')}")
                
                except Exception as e:
                    logger.error(f"Error processing company {company.get('name', 'Unknown')}: {str(e)}")
            
            logger.info(f"Successfully processed {success_count}/{len(companies)} ACT companies")
        
        except Exception as e:
            logger.error(f"Error processing ACT_COMPANIES: {str(e)}")

    async def get_act_companies_from_db(self):
        """Retrieve ACT companies from the database instead of constants"""
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/companies?select=*",
                headers=SUPABASE_HEADERS
            )
            if response.status_code == 200 and response.json():
                logger.info(f"Retrieved {len(response.json())} companies from database")
                return response.json()
            else:
                logger.warning("No companies found in database, using fallback")
                return ACT_COMPANIES
        except Exception as e:
            logger.error(f"Error retrieving companies from database: {e}")
            return ACT_COMPANIES
    
    async def process_sectors(self) -> None:
        """Process and insert sector data from constants.py."""
        logger.info("Starting sector data ingestion...")
        success_count = 0
        
        for sector_name in CLEAN_ENERGY_SECTORS:
            # Create a simple sector entry
            sector_data = {
                'name': sector_name,
                'description': f"Clean energy sector: {sector_name}"
            }
            
            # Insert sector
            if await self.insert_sector(sector_data):
                success_count += 1
                
                # Store sector data as a memory for vector search
                await self.store_memory(
                    f"Sector: {sector_name}\n\nDescription: {sector_data['description']}",
                    {
                        'source': 'constants.py',
                        'type': 'sector',
                        'sector_name': sector_name
                    }
                )
        
        logger.info(f"Successfully processed {success_count}/{len(CLEAN_ENERGY_SECTORS)} sectors")
    
    async def process_pathways(self) -> None:
        """Process and insert career pathway data from constants.py."""
        logger.info("Starting career pathway data ingestion...")
        success_count = 0
        
        for pathway in TRANSITION_PATHWAYS:
            # Store pathway data as a memory for vector search
            if await self.store_memory(
                f"Career Pathway: {pathway}",
                {
                    'source': 'constants.py',
                    'type': 'career_pathway',
                    'pathway': pathway
                }
            ):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count}/{len(TRANSITION_PATHWAYS)} career pathways")

async def main() -> None:
    """Main function to run the data ingestion process."""
    try:
        logger.info("Starting data ingestion process...")
        
        # Create ingester
        ingester = ClimateDataIngester()
        
        # Process documents only since constants.py doesn't have all the expected data
        logger.info("Starting document processing...")
        docs_path = Path(__file__).parent.parent / 'docs'
        await ingester.process_documents_directory(str(docs_path))
        
        logger.info("Data ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 