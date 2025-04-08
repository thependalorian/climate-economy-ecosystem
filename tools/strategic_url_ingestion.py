#!/usr/bin/env python3
"""
Strategic URL Ingestion - Implements multi-tiered approach for crawling climate economy ecosystem URLs.
"""

import os
import sys
import asyncio
import logging
import json
import time
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree
import tempfile
import urllib.request
from PyPDF2 import PdfReader
from openai import OpenAI
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from constants import CLIMATE_REPORT_RESOURCES

# Define our own ACT_COMPANIES list
ACT_COMPANIES = [
    {
        "name": "MassCEC",
        "url": "https://www.masscec.com/",
        "description": "Massachusetts Clean Energy Center - State economic development agency dedicated to accelerating the growth of the clean energy sector across Massachusetts.",
        "resources": [
            "https://www.masscec.com/workforce-development",
            "https://www.masscec.com/clean-energy-careers",
            "https://www.masscec.com/offshore-wind"
        ],
        "sector": "Economic Development"
    },
    {
        "name": "Greentown Labs",
        "url": "https://www.greentownlabs.com/",
        "description": "North America's largest climate tech startup incubator, headquartered in Somerville, MA.",
        "resources": [
            "https://www.greentownlabs.com/about/",
            "https://www.greentownlabs.com/startups/",
            "https://www.greentownlabs.com/careers/"
        ],
        "sector": "Innovation & Entrepreneurship"
    },
    {
        "name": "NECEC",
        "url": "https://www.necec.org/",
        "description": "Northeast Clean Energy Council - Business association and innovation network dedicated to growing the clean energy economy.",
        "resources": [
            "https://www.necec.org/focus-areas",
            "https://www.necec.org/careers"
        ],
        "sector": "Business Development"
    },
    {
        "name": "FranklinCummings",
        "url": "https://franklincummings.edu/",
        "description": "Franklin Cummings Tech - A leading technical college in Boston specializing in hands-on education for clean energy careers.",
        "resources": [
            "https://franklincummings.edu/academics/academic-programs/",
            "https://franklincummings.edu/academics/academic-programs/renewable-energy-technology/"
        ],
        "sector": "Education & Training"
    }
]

# Helper functions for company status tracking
def mark_company_as_indexed(company_name):
    """Mark a company as indexed in our local list."""
    for company in ACT_COMPANIES:
        if company["name"] == company_name:
            company["indexed"] = True
            return True
    return False

def save_company_index_status():
    """Save company indexing status to a local file."""
    status = {company["name"]: company.get("indexed", False) for company in ACT_COMPANIES}
    try:
        with open("company_index_status.json", "w") as f:
            json.dump(status, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving company index status: {str(e)}")
        return False

# Education resources
EDUCATION_RESOURCES = [
    "https://franklincummings.edu/academics/academic-programs/",
    "https://franklincummings.edu/academics/academic-programs/renewable-energy-technology/",
    "https://www.masscec.com/clean-energy-internships-students",
    "https://cleanenergyeducation.org/"
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('strategic_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Default system user ID
SYSTEM_USER_ID = "system"

# Initialize base headers for Supabase requests
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Organization types for specialized handling
ORGANIZATION_TYPES = {
    "government": ["MassCEC", "MassHire", "Massachusetts EEAC"],
    "education": ["FranklinCummings", "UMass Clean Energy Extension"],
    "innovation": ["Greentown Labs", "NECEC", "ACT"],
    "service": ["TPS Energy", "ULEM", "MyHeadlamp", "AfricanBN"]
}

# Define organization-specific strategies
ORG_STRATEGIES = {
    "government": {
        "priority_paths": ["/reports", "/programs", "/workforce", "/jobs", "/careers", "/clean-energy"],
        "content_threshold": 150,  # Longer content for government pages
        "chunk_size": 1200,
        "chunk_overlap": 250,
        "max_depth": 2,
        "delay": 3
    },
    "education": {
        "priority_paths": ["/academics", "/programs", "/courses", "/curriculum", "/training"],
        "content_threshold": 120,
        "chunk_size": 1000,
        "chunk_overlap": 300,  # Higher overlap for educational content
        "max_depth": 3,
        "delay": 2
    },
    "innovation": {
        "priority_paths": ["/startups", "/companies", "/members", "/portfolio", "/about", "/programs", "/initiatives"],
        "content_threshold": 100,
        "chunk_size": 900,
        "chunk_overlap": 200,
        "max_depth": 2,
        "delay": 2
    },
    "service": {
        "priority_paths": ["/services", "/about", "/what-we-do", "/careers", "/projects", "/programs"],
        "content_threshold": 80,
        "chunk_size": 800,
        "chunk_overlap": 150,
        "max_depth": 1,
        "delay": 1
    }
}

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

class StrategicURLIngester:
    """Strategic URL ingester for climate economy ecosystem - implements multi-tiered approach."""
    
    def __init__(self):
        """Initialize the strategic URL ingester."""
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize rate limiters
        self.supabase_rate_limiter = RateLimiter(2.0)  # 2 calls per second
        self.url_rate_limiter = RateLimiter(0.5)  # 1 call per 2 seconds
        
        # Browser headers
        self.browser_headers = {
            'User-Agent': 'Mozilla/5.0 Climate Economy Knowledge Crawler Bot (Contact: info@joinact.org)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Track processed URLs
        self.processed_urls: Set[str] = set()
        
        # Tier tracking - categorize URLs by their tier
        self.tier_1_urls: Set[str] = set()  # Primary (direct, high-value)
        self.tier_2_urls: Set[str] = set()  # Secondary (sitemap-discovered)
        self.tier_3_urls: Set[str] = set()  # Tertiary (link-discovered)
        
        # Success tracking
        self.success_count = 0
        self.failed_count = 0
        
    def get_organization_type(self, company_name: str) -> str:
        """Determine the organization type for a company name."""
        for org_type, companies in ORGANIZATION_TYPES.items():
            if company_name in companies:
                return org_type
        return "service"  # Default
    
    def get_strategy_for_company(self, company_name: str) -> Dict:
        """Get the appropriate strategy settings for a company."""
        org_type = self.get_organization_type(company_name)
        return ORG_STRATEGIES[org_type]
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"  # 1536 dimensions
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding with OpenAI: {str(e)}")
            return None
    
    def smart_chunker(self, text: str, strategy: Dict) -> List[str]:
        """Split text into chunks intelligently based on organization strategy."""
        # Get strategy parameters
        chunk_size = strategy.get("chunk_size", 1000)
        chunk_overlap = strategy.get("chunk_overlap", 200)
        
        # Enforce maximum content size limit
        MAX_CONTENT_SIZE = 200000  # ~200KB max content size
        if len(text) > MAX_CONTENT_SIZE:
            logger.warning(f"Content too large ({len(text)} chars), truncating to {MAX_CONTENT_SIZE} chars")
            text = text[:MAX_CONTENT_SIZE]
        
        # Clean up text
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        # Split text into meaningful segments
        segments = re.split(r'([.!?]\s+|\n{2,})', text)
        
        for i in range(0, len(segments), 2):
            segment = segments[i]
            # Add the punctuation/newline back if it exists
            if i + 1 < len(segments):
                segment += segments[i + 1]
                
            # If adding this segment would exceed chunk size, start new chunk
            if current_length + len(segment) > chunk_size and current_chunk:
                chunks.append(''.join(current_chunk).strip())
                
                # Start new chunk with overlap from previous
                overlap_start = max(0, len(''.join(current_chunk)) - chunk_overlap)
                current_chunk = [''.join(current_chunk)[overlap_start:]]
                current_length = len(current_chunk[0])
            
            current_chunk.append(segment)
            current_length += len(segment)
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(''.join(current_chunk).strip())
        
        # Limit to a reasonable number of chunks
        MAX_CHUNKS = 20
        if len(chunks) > MAX_CHUNKS:
            logger.warning(f"Too many chunks ({len(chunks)}), limiting to {MAX_CHUNKS}")
            chunks = chunks[:MAX_CHUNKS]
            
        return chunks
    
    def extract_structured_content(self, element) -> str:
        """Extract content while preserving structure (headings, lists, paragraphs)."""
        if not element:
            return ""
        
        # Dictionary to store the extracted content with structure preserved
        content = []
        
        # Process all elements recursively
        for child in element.find_all(recursive=False):
            # Handle different HTML elements to preserve structure
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Convert HTML headings to markdown headings
                level = int(child.name[1])
                heading_text = child.get_text(strip=True)
                content.append('\n' + '#' * level + ' ' + heading_text + '\n')
            
            elif child.name == 'p':
                # Handle paragraphs
                para_text = child.get_text(strip=True)
                if para_text:
                    content.append(para_text + '\n\n')
            
            elif child.name in ['ul', 'ol']:
                # Handle lists
                list_items = []
                for li in child.find_all('li', recursive=True):
                    li_text = li.get_text(strip=True)
                    prefix = '- ' if child.name == 'ul' else f"{len(list_items) + 1}. "
                    list_items.append(f"{prefix}{li_text}")
                
                if list_items:
                    content.append('\n' + '\n'.join(list_items) + '\n\n')
            
            elif child.name == 'pre' or child.name == 'code':
                # Handle code blocks
                code_text = child.get_text(strip=True)
                if code_text:
                    content.append('\n```\n' + code_text + '\n```\n\n')
            
            elif child.name == 'table':
                # Extract table content
                table_content = self.extract_table_content(child)
                if table_content:
                    content.append('\n' + table_content + '\n\n')
            
            elif child.name in ['div', 'section', 'article', 'main']:
                # Recursively process container elements
                nested_content = self.extract_structured_content(child)
                if nested_content:
                    content.append(nested_content)
            
            elif child.name in ['a']:
                # Handle links - add the text and the URL
                link_text = child.get_text(strip=True)
                link_url = child.get('href', '')
                if link_text and link_url:
                    content.append(f"{link_text} ")
            
            elif child.name in ['span', 'strong', 'em', 'b', 'i']:
                # Inline elements, just get the text
                inline_text = child.get_text(strip=True)
                if inline_text:
                    content.append(inline_text + ' ')
        
        # If no structured content is found, fall back to simple text extraction
        if not content and element.get_text(strip=True):
            return element.get_text(separator='\n', strip=True)
        
        return '\n'.join(content)
    
    def extract_table_content(self, table_element) -> str:
        """Extract content from table element in a readable format."""
        if not table_element:
            return ""
            
        table_content = []
        
        # Extract headers
        headers = []
        header_row = table_element.find('thead')
        if header_row:
            th_elements = header_row.find_all('th')
            if th_elements:
                headers = [th.get_text(strip=True) for th in th_elements]
                table_content.append("| " + " | ".join(headers) + " |")
                table_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # Extract rows
        rows = table_element.find_all('tr')
        for row in rows:
            # Skip header rows that we've already processed
            if row.find_parent('thead'):
                continue
                
            cells = row.find_all(['td', 'th'])
            if cells:
                row_content = "| " + " | ".join([cell.get_text(strip=True) for cell in cells]) + " |"
                table_content.append(row_content)
        
        return "\n".join(table_content) if table_content else "Table content (simplified)"
    
    async def memory_exists(self, url: str, chunk_index: Optional[int] = None) -> bool:
        """Check if a memory with the given URL and chunk index already exists."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Build metadata query
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
    
    async def store_memory(self, content: str, metadata: Dict) -> bool:
        """Store a memory in the climate_memories table with embedding."""
        try:
            await self.supabase_rate_limiter.wait()
            
            # Skip if content is too short
            if not content or len(content.strip()) < metadata.get("content_threshold", 50):
                logger.warning(f"Content too short, skipping: {metadata.get('url', 'unknown')}")
                return False
            
            # Check if memory already exists
            if 'url' in metadata:
                chunk_index = metadata.get('chunk_index')
                if await self.memory_exists(metadata['url'], chunk_index):
                    logger.info(f"Memory for {metadata['url']} (chunk {chunk_index}) already exists, skipping")
                    return True  # Consider it a success
            
            # Create memory data
            memory_data = {
                'content': content,
                'user_id': SYSTEM_USER_ID,  # Required field
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
                logger.info(f"Successfully inserted memory: {metadata.get('title', 'unknown')} from {metadata.get('url', 'unknown')}")
                return True
            else:
                logger.error(f"Failed to insert memory: {response.status_code} {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return False
    
    async def download_and_process_pdf(self, url: str, company_name: str = None) -> Optional[Dict]:
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
                
                # Determine organization type for strategy if company is known
                org_type = "government"  # Default for PDF documents
                if company_name:
                    org_type = self.get_organization_type(company_name)
                    
                strategy = ORG_STRATEGIES[org_type]
                
                # Build response
                return {
                    'content': content,
                    'strategy': strategy,
                    'metadata': {
                        **metadata,
                        'file_type': 'pdf',
                        'url': url,
                        'file_name': url.split('/')[-1],
                        'num_pages': len(reader.pages),
                        'organization': company_name,
                        'organization_type': org_type,
                        'tier': 1,  # PDF documents are always tier 1
                        'extraction_method': 'pdf_extract',
                        'indexed_at': datetime.now(timezone.utc).isoformat(),
                        'content_threshold': strategy['content_threshold']
                    }
                }
        
        except Exception as e:
            logger.error(f"Error downloading and processing PDF from {url}: {str(e)}")
            return None
    
    async def process_webpage(self, url: str, company_name: str = None, tier: int = 1) -> Optional[Dict]:
        """Process a webpage using enhanced extraction."""
        try:
            logger.info(f"Processing webpage: {url} (Tier {tier})")
            
            # Wait for rate limiting
            await self.url_rate_limiter.wait()
            
            # Determine organization type for customized processing
            org_type = "service"  # Default
            if company_name:
                org_type = self.get_organization_type(company_name)
                
            strategy = ORG_STRATEGIES[org_type]
            
            # Fetch the webpage
            response = requests.get(url, headers=self.browser_headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract the domain
            domain = urlparse(url).netloc
            
            # Extract the title
            title = soup.title.string if soup.title else url.split('/')[-1]
            
            # Find main content area - apply different strategies based on organization type
            main_content = None
            
            if org_type == "government":
                # Government sites often have main content in specific containers
                main_content = (
                    soup.find('main') or 
                    soup.find('article') or 
                    soup.find('div', id='content') or
                    soup.find('div', class_='content-area') or
                    soup.find('div', class_='main-content')
                )
            elif org_type == "education":
                # Education sites often have program information in specific areas
                main_content = (
                    soup.find('div', id='program-content') or
                    soup.find('div', class_='program') or
                    soup.find('article') or
                    soup.find('div', class_='course-description') or
                    soup.find('main')
                )
            else:
                # Default content extraction strategy
                main_content = (
                    soup.find('main') or 
                    soup.find('article') or 
                    soup.find('div', class_='content') or 
                    soup.find('div', id='content') or
                    soup
                )
            
            # Extract structured content
            text = self.extract_structured_content(main_content or soup)
            
            # Clean up text
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'\s{2,}', ' ', text)
            
            logger.info(f"Successfully processed webpage: {url}")
            
            # Look for and collect links for tier 3 processing (only for tier 1 and 2 pages)
            additional_urls = []
            if tier < 3:  # Only collect links from tier 1 and 2 pages
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    # Skip non-HTTP, anchors, or external links
                    if not href.startswith('http') and not href.startswith('/'):
                        continue
                    if href.startswith('#'):
                        continue
                        
                    # Resolve relative URLs
                    if href.startswith('/'):
                        href = urljoin(url, href)
                        
                    # Skip if not same domain
                    if urlparse(href).netloc != domain:
                        continue
                        
                    # Only consider URLs that match priority paths for this org type
                    if any(path in href.lower() for path in strategy['priority_paths']):
                        additional_urls.append(href)
            
            # Build response
            return {
                'content': text,
                'additional_urls': list(set(additional_urls)),  # Deduplicate
                'strategy': strategy,
                'metadata': {
                    'file_type': 'webpage',
                    'url': url,
                    'title': title,
                    'domain': domain,
                    'organization': company_name,
                    'organization_type': org_type,
                    'tier': tier,
                    'extraction_method': 'html_structured',
                    'indexed_at': datetime.now(timezone.utc).isoformat(),
                    'content_threshold': strategy['content_threshold']
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing webpage {url}: {str(e)}")
            return None
    
    async def process_url(self, url: str, company_name: str = None, tier: int = 1) -> Tuple[bool, List[str]]:
        """Process a URL with the appropriate method based on type."""
        try:
            # Skip if already processed
            if url in self.processed_urls:
                logger.info(f"URL {url} already processed, skipping")
                return True, []
                
            # Check if URL already exists in database
            if await self.memory_exists(url, None):
                logger.info(f"URL {url} already exists in database, skipping")
                self.processed_urls.add(url)
                return True, []
                
            # Track URL in the appropriate tier
            if tier == 1:
                self.tier_1_urls.add(url)
            elif tier == 2:
                self.tier_2_urls.add(url)
            elif tier == 3:
                self.tier_3_urls.add(url)
            
            # Determine how to process the URL
            additional_urls = []
            if url.lower().endswith('.pdf'):
                # Process PDF
                result = await self.download_and_process_pdf(url, company_name)
            else:
                # Process webpage
                result = await self.process_webpage(url, company_name, tier)
                if result:
                    additional_urls = result.get('additional_urls', [])
            
            # Mark as processed regardless of outcome
            self.processed_urls.add(url)
            
            if not result:
                logger.error(f"Failed to process URL: {url}")
                self.failed_count += 1
                return False, []
            
            # Get the strategy from the result
            strategy = result.get('strategy')
            
            # Get the content
            content = result.get('content')
            
            # For long content, split into chunks
            if len(content) > strategy.get('chunk_size', 1000):
                chunks = self.smart_chunker(content, strategy)
                logger.info(f"Split content into {len(chunks)} chunks")
                
                # Store each chunk as a separate memory
                success_count = 0
                for i, chunk in enumerate(chunks):
                    # Add chunk metadata
                    chunk_metadata = {
                        **result.get('metadata', {}),
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                    
                    # Store the chunk
                    if await self.store_memory(chunk, chunk_metadata):
                        success_count += 1
                
                logger.info(f"Successfully stored {success_count}/{len(chunks)} chunks from {url}")
                if success_count > 0:
                    self.success_count += 1
                    return True, additional_urls
                else:
                    self.failed_count += 1
                    return False, []
            else:
                # Store single document
                if await self.store_memory(content, result.get('metadata', {})):
                    logger.info(f"Successfully stored content from {url}")
                    self.success_count += 1
                    return True, additional_urls
                else:
                    logger.error(f"Failed to store content from {url}")
                    self.failed_count += 1
                    return False, []
                
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            # Mark as processed to avoid re-processing on failure
            self.processed_urls.add(url)
            self.failed_count += 1
            return False, []
    
    async def process_company(self, company: Dict) -> int:
        """Process a company using multi-tiered approach."""
        company_name = company.get('name', '')
        company_url = company.get('url', '')
        company_resources = company.get('resources', [])
        
        if not company_url:
            logger.warning(f"No URL for company: {company_name}")
            return 0
            
        logger.info(f"Processing company: {company_name}")
        success_count = 0
        total_count = 0
        additional_urls = []
        
        # Determine organization type and strategy
        org_type = self.get_organization_type(company_name)
        strategy = ORG_STRATEGIES[org_type]
        logger.info(f"Using {org_type} strategy for {company_name}")
        
        # TIER 1: Process main company page
        logger.info(f"TIER 1: Processing main company URL: {company_url}")
        success, urls = await self.process_url(company_url, company_name, 1)
        if success:
            success_count += 1
        total_count += 1
        additional_urls.extend(urls)
        
        # TIER 1: Process explicit resource URLs
        for resource_url in company_resources:
            if resource_url != company_url and resource_url.startswith('http'):
                logger.info(f"TIER 1: Processing resource URL: {resource_url}")
                success, urls = await self.process_url(resource_url, company_name, 1)
                if success:
                    success_count += 1
                total_count += 1
                additional_urls.extend(urls)
            
            # Respect delay between URLs
            await asyncio.sleep(strategy["delay"])
        
        # TIER 3: Process discovered URLs (limited depth)
        if additional_urls:
            # Limit the number of additional URLs to process
            max_additional = min(10, len(additional_urls))
            logger.info(f"TIER 3: Processing {max_additional} discovered URLs (out of {len(additional_urls)})")
            
            for i, discovered_url in enumerate(additional_urls[:max_additional]):
                if discovered_url not in self.processed_urls:
                    logger.info(f"TIER 3: Processing discovered URL ({i+1}/{max_additional}): {discovered_url}")
                    success, _ = await self.process_url(discovered_url, company_name, 3)
                    if success:
                        success_count += 1
                    total_count += 1
                
                # Respect delay between URLs
                await asyncio.sleep(strategy["delay"])
        
        logger.info(f"Completed processing for {company_name}: {success_count}/{total_count} successful")
        
        # Mark company as indexed if at least one URL was successful
        if success_count > 0:
            try:
                mark_company_as_indexed(company_name)
                save_company_index_status()
                logger.info(f"Marked {company_name} as indexed")
            except Exception as e:
                logger.warning(f"Could not mark company as indexed: {str(e)}")
                
        return success_count
    
    async def process_all_companies(self) -> int:
        """Process all companies using the strategic approach."""
        logger.info("Processing all companies using strategic approach...")
        
        total_success = 0
        
        # Process each company
        for i, company in enumerate(ACT_COMPANIES):
            logger.info(f"Processing company {i+1}/{len(ACT_COMPANIES)}")
            success_count = await self.process_company(company)
            total_success += success_count
            
            # Add delay between companies
            await asyncio.sleep(5)
            
        logger.info(f"Completed processing all companies: {total_success} successful URLs")
        return total_success
    
    async def process_climate_reports(self) -> int:
        """Process climate report URLs."""
        logger.info("Processing climate report URLs...")
        success_count = 0
        total_count = 0
        
        for report_url in CLIMATE_REPORT_RESOURCES:
            # Skip if not HTTP URL
            if not report_url.startswith('http'):
                continue
                
            logger.info(f"Processing climate report: {report_url}")
            success, _ = await self.process_url(report_url, None, 1)  # Climate reports are tier 1
            if success:
                success_count += 1
            total_count += 1
            
            # Add delay
            await asyncio.sleep(3)
                
        logger.info(f"Completed processing climate reports: {success_count}/{total_count} successful")
        return success_count
    
    async def process_education_resources(self) -> int:
        """Process education resource URLs."""
        logger.info("Processing education resource URLs...")
        success_count = 0
        total_count = 0
        
        for resource_url in EDUCATION_RESOURCES:
            # Skip if not HTTP URL
            if not resource_url.startswith('http'):
                continue
                
            # Determine associated company (if any)
            company_name = None
            for company in ACT_COMPANIES:
                if company.get('sector') == 'Education & Training' and resource_url.startswith(company.get('url', '')):
                    company_name = company.get('name')
                    break
            
            logger.info(f"Processing education resource: {resource_url}")
            success, _ = await self.process_url(resource_url, company_name, 1)  # Education resources are tier 1
            if success:
                success_count += 1
            total_count += 1
            
            # Add delay
            await asyncio.sleep(2)
                
        logger.info(f"Completed processing education resources: {success_count}/{total_count} successful")
        return success_count
    
    def print_summary(self):
        """Print a summary of processed URLs by tier."""
        print("\n" + "="*50)
        print("STRATEGIC URL INGESTION SUMMARY")
        print("="*50)
        print(f"Total processed URLs: {len(self.processed_urls)}")
        print(f"Successfully stored: {self.success_count}")
        print(f"Failed to store: {self.failed_count}")
        print("\nURLs by tier:")
        print(f"  Tier 1 (Primary): {len(self.tier_1_urls)}")
        print(f"  Tier 2 (Secondary): {len(self.tier_2_urls)}")
        print(f"  Tier 3 (Tertiary): {len(self.tier_3_urls)}")
        print("="*50 + "\n")

async def main():
    """Main function to run the strategic URL ingestion."""
    ingester = None
    try:
        logger.info("Starting strategic URL ingestion...")
        
        # Create the strategic ingester
        ingester = StrategicURLIngester()
        
        # Process in priority order: reports, companies, education resources
        
        # First: Process climate reports
        await ingester.process_climate_reports()
        
        # Second: Process company websites
        await ingester.process_all_companies()
        
        # Third: Process education resources
        await ingester.process_education_resources()
        
        # Print summary
        ingester.print_summary()
        
        logger.info("Strategic URL ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during strategic URL ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 