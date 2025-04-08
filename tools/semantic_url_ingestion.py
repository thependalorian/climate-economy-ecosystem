#!/usr/bin/env python3
"""
Semantic URL Ingestion Tool - Uses Crawl4AI with Cosine Strategy for intelligent content extraction.
Specializes in extracting climate economy related content from websites.
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
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree
import tempfile
import urllib.request
from PyPDF2 import PdfReader
from openai import OpenAI
from bs4 import BeautifulSoup

# Import crawl4ai components with all required strategies
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
    from crawl4ai.deep_crawling.filters import FilterChain, ContentTypeFilter, SEOFilter, DomainFilter
    from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
    from crawl4ai.extraction_strategy import CosineStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("crawl4ai not available. Install with: pip install crawl4ai[torch]")
    print("Then run: crawl4ai-setup")
    # Define dummy classes for type hinting when crawl4ai is not available
    class AsyncWebCrawler: pass
    class BrowserConfig: pass
    class CrawlerRunConfig: pass
    class DefaultMarkdownGenerator: pass
    class CosineStrategy: pass

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))
try:
    from constants import CLIMATE_REPORT_RESOURCES
    
    # Define climate-related keywords for semantic filtering
    CLIMATE_KEYWORDS = [
        "clean energy", "renewable energy", "climate tech", "sustainability",
        "climate economy", "green jobs", "carbon reduction", "net zero",
        "climate innovation", "solar", "wind power", "energy efficiency"
    ]
except ImportError:
    CLIMATE_REPORT_RESOURCES = ["https://www.masscec.com/reports/industry-2023/"]
    CLIMATE_KEYWORDS = ["clean energy", "renewable energy", "climate tech"]
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('semantic_url_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
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

# Define our own company list since we can't import from constants
ACT_COMPANIES = [
    {
        "name": "MassCEC",
        "url": "https://www.masscec.com/",
        "description": "Massachusetts Clean Energy Center - State economic development agency dedicated to accelerating the growth of the clean energy sector across Massachusetts.",
        "resources": [
            "https://www.masscec.com/workforce-development",
            "https://www.masscec.com/clean-energy-careers",
            "https://www.masscec.com/offshore-wind"
        ]
    },
    {
        "name": "Greentown Labs",
        "url": "https://www.greentownlabs.com/",
        "description": "North America's largest climate tech startup incubator, headquartered in Somerville, MA.",
        "resources": [
            "https://www.greentownlabs.com/about/",
            "https://www.greentownlabs.com/startups/",
            "https://www.greentownlabs.com/careers/"
        ]
    },
    {
        "name": "NECEC",
        "url": "https://www.necec.org/",
        "description": "Northeast Clean Energy Council - Business association and innovation network dedicated to growing the clean energy economy.",
        "resources": [
            "https://www.necec.org/focus-areas",
            "https://www.necec.org/careers"
        ]
    }
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

class SemanticURLIngester:
    """Semantic Climate Economy Ecosystem URL ingester with crawl4ai Cosine Strategy."""
    
    def __init__(self):
        """Initialize the URL ingester."""
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize rate limiters
        self.supabase_rate_limiter = RateLimiter(2.0)  # 2 calls per second
        self.url_rate_limiter = RateLimiter(0.5)  # 1 call per 2 seconds to be respectful
        
        # Configuration for processing
        self.chunk_size = 1000
        self.chunk_overlap = 200
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
        
        # Create extraction strategies based on content type
        if CRAWL4AI_AVAILABLE:
            self.create_extraction_strategies()
            
            # Set up browser config for crawl4ai
            self.browser_config = BrowserConfig(
                headless=True,
                ignore_https_errors=True,
                default_timeout=60000,  # 60 seconds
                user_agent=self.browser_headers['User-Agent'],
                viewport_width=1280,
                viewport_height=800
            )
            
            # Create crawler semaphore for concurrency control
            self.crawler_semaphore = asyncio.Semaphore(2)  # Max parallel crawlers
            self.active_crawlers = set()
            self.crawling_tasks = set()
            self.should_exit = False
    
    def create_extraction_strategies(self):
        """Create specialized extraction strategies for different content types."""
        
        # General climate content strategy - medium match threshold
        self.general_climate_strategy = CosineStrategy(
            semantic_filter=" ".join(CLIMATE_KEYWORDS[:5]),  # Use first 5 keywords
            word_count_threshold=30,  # Medium length content
            sim_threshold=0.4,        # Medium similarity threshold
            top_k=5                   # Get multiple content blocks
        )
        
        # Company/organization information strategy - stricter matching
        self.company_info_strategy = CosineStrategy(
            semantic_filter="company information mission values team leadership sustainability initiatives",
            word_count_threshold=50,   # Longer content for company info
            sim_threshold=0.5,         # Higher similarity
            top_k=3                    # Fewer top matches
        )
        
        # Research/technical content strategy - strict matching
        self.research_strategy = CosineStrategy(
            semantic_filter="climate research data analysis technical reports results findings study",
            word_count_threshold=100,  # Longer content for research
            sim_threshold=0.6,         # Strict matching
            top_k=2                    # Focus on main content
        )
    
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
        # Enforce maximum content size limit to prevent memory issues
        MAX_CONTENT_SIZE = 200000  # ~200KB max content size
        if len(text) > MAX_CONTENT_SIZE:
            logger.warning(f"Content too large ({len(text)} chars), truncating to {MAX_CONTENT_SIZE} chars")
            text = text[:MAX_CONTENT_SIZE]
            
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
        
        # Limit chunks to avoid excessive processing
        MAX_CHUNKS = 20  # Limit chunks to be reasonable
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
                        'indexed_at': datetime.now(timezone.utc).isoformat(),
                        'extraction_method': 'pdf_extract'
                    }
                }
        
        except Exception as e:
            logger.error(f"Error downloading and processing PDF from {url}: {str(e)}")
            return None
    
    def determine_content_type(self, url: str) -> str:
        """Determine the type of content on the URL to select appropriate extraction strategy."""
        url_lower = url.lower()
        
        # Research pages typically contain these terms
        if any(term in url_lower for term in ['/research', '/publication', '/report', '/whitepaper', '/study']):
            return 'research'
            
        # Company/about pages
        if any(term in url_lower for term in ['/about', '/company', '/team', '/leadership', '/mission']):
            return 'company'
            
        # Default to general
        return 'general'
    
    def select_extraction_strategy(self, content_type: str) -> CosineStrategy:
        """Select appropriate extraction strategy based on content type."""
        if content_type == 'research':
            return self.research_strategy
        elif content_type == 'company':
            return self.company_info_strategy
        else:
            return self.general_climate_strategy
    
    async def process_webpage_with_crawl4ai(self, url: str) -> Optional[Dict]:
        """Process a webpage using crawl4ai with Cosine Strategy for better content extraction."""
        if not CRAWL4AI_AVAILABLE:
            logger.warning("crawl4ai not available, falling back to basic HTML processing")
            return None
            
        # Acquire semaphore to limit concurrency
        async with self.crawler_semaphore:
            crawler = None
            try:
                logger.info(f"Processing webpage with crawl4ai: {url}")
                
                # Determine content type for strategy selection
                content_type = self.determine_content_type(url)
                logger.info(f"Determined content type: {content_type} for {url}")
                
                # Select appropriate extraction strategy
                extraction_strategy = self.select_extraction_strategy(content_type)
                
                # Initialize crawler
                crawler = AsyncWebCrawler(config=self.browser_config)
                self.active_crawlers.add(crawler)
                
                # Start the browser with timeout
                try:
                    start_task = asyncio.create_task(crawler.start())
                    await asyncio.wait_for(start_task, timeout=60)
                    await asyncio.sleep(1)  # Give browser time to stabilize
                except asyncio.TimeoutError:
                    logger.error(f"Browser startup timed out for {url}")
                    return None
                
                # Configure crawler run with the selected extraction strategy
                crawler_config = CrawlerRunConfig(
                    page_timeout=90000,          # 90 seconds timeout
                    wait_for_network_idle=True,  # Wait for network to be idle
                    wait_for_timeout=5000,       # Additional 5s wait after loading
                    extract_markdown=True,       # Get markdown content
                    markdown_generator=DefaultMarkdownGenerator(),
                    extraction_strategy=extraction_strategy  # Use our semantic strategy
                )
                
                # Crawl the page
                result = None
                try:
                    crawl_task = asyncio.create_task(crawler.arun(url=url, config=crawler_config))
                    self.crawling_tasks.add(crawl_task)
                    result = await asyncio.wait_for(crawl_task, timeout=120)  # 2 minute timeout
                    if crawl_task in self.crawling_tasks:
                        self.crawling_tasks.remove(crawl_task)
                except asyncio.TimeoutError:
                    logger.error(f"Crawling {url} timed out")
                    return None
                except asyncio.CancelledError:
                    logger.info(f"Crawling task for {url} was cancelled")
                    return None
                finally:
                    if crawl_task in self.crawling_tasks:
                        self.crawling_tasks.remove(crawl_task)
                
                # Check result
                if not result:
                    logger.warning(f"No result returned for {url}")
                    return None
                    
                if not hasattr(result, 'success') or not result.success:
                    error_message = getattr(result, 'error_message', 'Unknown error')
                    logger.error(f"Failed to crawl {url}: {error_message}")
                    return None
                
                # Extract content using preferred content sources - try extracted_content first
                content = None
                extraction_method = None
                
                try:
                    # Try getting content from the extraction strategy first
                    if hasattr(result, 'extracted_content') and result.extracted_content:
                        content = result.extracted_content
                        extraction_method = f"cosine_strategy_{content_type}"
                        logger.info(f"Using extracted content from Cosine Strategy for {url}")
                    
                    # Next try the markdown_v2 which is richer
                    elif (hasattr(result, 'markdown_v2') and result.markdown_v2 is not None and 
                          hasattr(result.markdown_v2, 'raw_markdown') and result.markdown_v2.raw_markdown):
                        content = result.markdown_v2.raw_markdown
                        extraction_method = "markdown_v2"
                        logger.info(f"Using markdown_v2 content for {url}")
                    
                    # Fall back to basic markdown
                    elif hasattr(result, 'markdown') and result.markdown:
                        content = result.markdown
                        extraction_method = "markdown"
                        logger.info(f"Using basic markdown content for {url}")
                    
                    # Last resort - raw HTML
                    elif hasattr(result, 'html') and result.html:
                        soup = BeautifulSoup(result.html, 'html.parser')
                        # Remove unwanted elements
                        for element in soup(["script", "style", "nav", "footer", "header"]):
                            element.decompose()
                        content = soup.get_text(separator='\n', strip=True)
                        extraction_method = "html_fallback"
                        logger.info(f"Using HTML fallback content for {url}")
                    else:
                        logger.warning(f"No content found in result for {url}")
                        return None
                except Exception as e:
                    logger.error(f"Error extracting content from {url}: {str(e)}")
                    return None
                
                # Extract title
                title = url.split("/")[-1]  # Default to URL path
                try:
                    # Try to extract title from HTML if available
                    if hasattr(result, 'html') and result.html:
                        soup = BeautifulSoup(result.html, 'html.parser')
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.get_text(strip=True)
                    # Try from first heading in markdown
                    else:
                        first_heading = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                        if first_heading:
                            title = first_heading.group(1).strip()
                except Exception:
                    # Use default title on error
                    pass
                
                return {
                    'content': content,
                    'metadata': {
                        'file_type': 'webpage',
                        'url': url,
                        'title': title,
                        'domain': urlparse(url).netloc,
                        'content_type': content_type,
                        'extraction_method': extraction_method,
                        'indexed_at': datetime.now(timezone.utc).isoformat()
                    }
                }
                
            except Exception as e:
                logger.error(f"Error processing {url} with crawl4ai: {str(e)}")
                return None
            finally:
                # Clean up resources
                if crawler:
                    try:
                        if crawler in self.active_crawlers:
                            self.active_crawlers.remove(crawler)
                        
                        # Close the crawler
                        if hasattr(crawler, 'stop') and callable(crawler.stop):
                            await crawler.stop()
                    except Exception as e:
                        logger.error(f"Error closing crawler: {str(e)}")
    
    async def process_webpage_fallback(self, url: str) -> Optional[Dict]:
        """Process a webpage using requests and BeautifulSoup as fallback when crawl4ai isn't available."""
        try:
            logger.info(f"Processing webpage with fallback method: {url}")
            
            # Wait for rate limiting
            await self.url_rate_limiter.wait()
            
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
            
            # Find main content area
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_='content') or 
                soup.find('div', id='content') or
                soup
            )
            
            # Extract structured content
            text = self.extract_structured_content(main_content)
            
            # Clean up text
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'\s{2,}', ' ', text)
            
            logger.info(f"Successfully processed webpage with fallback method: {url}")
            
            # Determine content type for metadata
            content_type = self.determine_content_type(url)
            
            return {
                'content': text,
                'metadata': {
                    'file_type': 'webpage',
                    'url': url,
                    'title': title,
                    'domain': domain,
                    'content_type': content_type,
                    'extraction_method': 'html_fallback',
                    'indexed_at': datetime.now(timezone.utc).isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error processing webpage with fallback method {url}: {str(e)}")
            return None
    
    async def process_url(self, url: str, source_type: str = 'report', organization: str = None) -> bool:
        """Process a URL (either webpage or PDF) with semantic extraction."""
        try:
            # Skip if already processed
            if url in self.processed_urls:
                logger.info(f"URL {url} already processed, skipping")
                return True
                
            # Check if URL already exists in database
            if await self.memory_exists(url):
                logger.info(f"URL {url} already exists in database, skipping")
                self.processed_urls.add(url)
                return True
                
            # Determine how to process the URL
            if url.lower().endswith('.pdf'):
                # Process PDF using PyPDF2
                result = await self.download_and_process_pdf(url)
            else:
                # Use crawl4ai with Cosine Strategy
                result = await self.process_webpage_with_crawl4ai(url)
                
                # If crawl4ai fails or isn't available, we'll need a fallback method
                if not result:
                    logger.warning(f"Crawl4AI processing failed for {url}, using fallback method")
                    result = await self.process_webpage_fallback(url)
                
            # Mark as processed regardless of outcome
            self.processed_urls.add(url)
            
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
            # Mark as processed to avoid re-processing on failure
            self.processed_urls.add(url)
            return False
    
    async def process_urls(self, urls: List[str], source_type: str = 'report', organization: str = None) -> int:
        """Process multiple URLs with throttling to respect servers."""
        if not urls:
            return 0
            
        logger.info(f"Processing {len(urls)} URLs as {source_type}")
        success_count = 0
        
        # Process in batches with delays between requests
        batch_size = 3
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i+batch_size]
            
            # Process each URL in batch
            for url in batch:
                if await self.process_url(url, source_type, organization):
                    success_count += 1
                    
                # Add delay between URLs to be respectful
                await asyncio.sleep(2)
                
            # Add delay between batches
            if i + batch_size < len(urls):
                logger.info(f"Processed {i+len(batch)}/{len(urls)} URLs, pausing before next batch")
                await asyncio.sleep(5)
                
        logger.info(f"Successfully processed {success_count}/{len(urls)} URLs")
        return success_count
    
    async def process_climate_reports(self) -> int:
        """Process all climate report URLs using semantic extraction."""
        # Filter to only include web URLs (not local files)
        web_urls = [url for url in CLIMATE_REPORT_RESOURCES if url.startswith('http')]
        
        if not web_urls:
            logger.warning("No web URLs found in CLIMATE_REPORT_RESOURCES")
            return 0
            
        return await self.process_urls(web_urls, 'climate_report')
    
    async def cleanup(self):
        """Clean up resources before exiting."""
        if not CRAWL4AI_AVAILABLE:
            return
            
        logger.info("Cleaning up resources...")
        
        # Close all active crawlers
        for crawler in list(self.active_crawlers):
            try:
                if hasattr(crawler, 'stop') and callable(crawler.stop):
                    await crawler.stop()
            except Exception as e:
                logger.error(f"Error stopping crawler: {str(e)}")
                
        # Cancel all tasks
        for task in list(self.crawling_tasks):
            if not task.done():
                task.cancel()
        
        # Wait for a moment to let tasks cancel
        await asyncio.sleep(1)
        
        logger.info("Cleanup completed")

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
                # Handle tables (simplified)
                content.append('\n[Table content]\n\n')
            
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

    async def process_companies_with_sitemaps(self) -> int:
        """Process ACT company websites using sitemaps for comprehensive coverage."""
        logger.info("Processing ACT company websites using sitemaps...")
        
        total_success = 0
        company_count = 0
        
        # Process each company
        for company in ACT_COMPANIES:
            company_name = company.get('name', '')
            base_url = company.get('url', '')
            
            if not base_url or not base_url.startswith('http'):
                logger.warning(f"Invalid or missing URL for company: {company_name}")
                continue
            
            company_count += 1
            logger.info(f"Processing company {company_count}/{len(ACT_COMPANIES)}: {company_name}")
            
            # Process the main page first
            logger.info(f"Processing main company page: {base_url}")
            if await self.process_url(base_url, 'company_website', company_name):
                total_success += 1
            
            # Try to discover sitemap
            sitemap_url = await self.auto_discover_sitemap(base_url)
            
            if sitemap_url:
                logger.info(f"Discovered sitemap for {company_name}: {sitemap_url}")
                
                # Page patterns to prioritize for companies
                important_patterns = [
                    # About pages
                    "/about", "/team", "/leadership", "/mission", "/vision", "/history",
                    # Career pages
                    "/careers", "/jobs", "/employment", "/opportunities", "/work-with-us",
                    # Service/product pages
                    "/services", "/solutions", "/products", "/offerings", "/what-we-do",
                    # Impact/sustainability pages
                    "/impact", "/sustainability", "/climate", "/esg", "/green", 
                    # Project pages
                    "/projects", "/case-studies", "/portfolio", "/success-stories"
                ]
                
                # Create a regex pattern to match any of these important pages
                filter_pattern = "|".join(important_patterns)
                
                # Process sitemap with filtering for important pages
                success_count = await self.process_sitemap_urls(
                    sitemap_url,
                    filter_pattern=filter_pattern,
                    source_type='company_website',
                    organization=company_name
                )
                
                logger.info(f"Processed {success_count} sitemap URLs for {company_name}")
                total_success += success_count
                
                # Try to mark the company as indexed if we got some content
                if success_count > 0:
                    try:
                        # Import and use the helper function if available
                        from constants import mark_company_as_indexed, save_company_index_status
                        mark_company_as_indexed(company_name)
                        save_company_index_status()
                    except ImportError:
                        logger.warning("Could not mark company as indexed - functions not available")
            else:
                logger.warning(f"No sitemap found for {company_name}, using direct URLs only")
                
                # Process additional resource URLs for this company
                resource_urls = company.get('resources', [])
                if resource_urls:
                    for url in resource_urls:
                        if url != base_url and url.startswith('http'):  # Skip if it's the main URL or not http
                            if await self.process_url(url, 'company_resource', company_name):
                                total_success += 1
            
            # Add a delay between companies to be respectful
            logger.info(f"Completed processing for {company_name}")
            await asyncio.sleep(5)
        
        logger.info(f"Finished processing {company_count} companies with {total_success} successful page ingestions")
        return total_success

    async def process_sitemap_urls(self, sitemap_url: str, filter_pattern: str = "", source_type: str = "website", organization: str = None) -> int:
        """Process all URLs from a sitemap for a specific organization."""
        try:
            # Fetch URLs from sitemap
            urls = await self.fetch_urls_from_sitemap(sitemap_url, filter_pattern)
            
            if not urls:
                logger.warning(f"No URLs found in sitemap for {organization or 'unknown'}")
                return 0

            logger.info(f"Starting crawl for {organization or 'unknown'} from sitemap")
            logger.info(f"Found {len(urls)} URLs to process")
            
            # Process URLs in batches to be gentler on target sites
            batch_size = 5
            total_processed = 0
            
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                batch_success = 0
                
                # Process each URL in batch
                for url in batch_urls:
                    if await self.process_url(url, source_type, organization):
                        batch_success += 1
                        total_processed += 1
                    
                    # Add delay between URLs
                    await asyncio.sleep(2)
                
                logger.info(f"Batch {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1}: Processed {batch_success}/{len(batch_urls)} URLs")
                
                # Add delay between batches
                if i + batch_size < len(urls):
                    logger.info(f"Processed {i+len(batch_urls)}/{len(urls)} URLs, pausing before next batch")
                    await asyncio.sleep(5)
            
            logger.info(f"Completed processing {total_processed}/{len(urls)} URLs for {organization or 'unknown'}")
            return total_processed
            
        except Exception as e:
            logger.error(f"Error processing sitemap {sitemap_url}: {str(e)}")
            return 0

    async def auto_discover_sitemap(self, base_url: str) -> Optional[str]:
        """Try to auto-discover sitemap URL from a base URL."""
        try:
            logger.info(f"Attempting to discover sitemap for {base_url}")
            
            # Common sitemap locations
            potential_paths = [
                "/sitemap.xml",
                "/sitemap_index.xml",
                "/sitemap.xml.gz",
                "/sitemap/sitemap.xml",
                "/sitemap.php",
                "/sitemap.txt"
            ]
            
            # Try each potential location
            for path in potential_paths:
                sitemap_url = urljoin(base_url, path)
                
                # Wait for rate limiter
                await self.url_rate_limiter.wait()
                
                try:
                    response = requests.get(sitemap_url, headers=self.browser_headers, timeout=10)
                    if response.status_code == 200:
                        # Check if it's a valid XML file
                        try:
                            ElementTree.fromstring(response.content)
                            logger.info(f"Discovered sitemap at {sitemap_url}")
                            return sitemap_url
                        except ElementTree.ParseError:
                            logger.debug(f"Found {sitemap_url} but not valid XML")
                            continue
                except Exception:
                    continue
                
            # Try robots.txt as fallback
            robots_url = urljoin(base_url, "/robots.txt")
            
            try:
                response = requests.get(robots_url, headers=self.browser_headers, timeout=10)
                if response.status_code == 200:
                    # Look for Sitemap directive in robots.txt
                    for line in response.text.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            logger.info(f"Found sitemap in robots.txt: {sitemap_url}")
                            return sitemap_url
            except Exception:
                pass
            
            logger.warning(f"Could not discover sitemap for {base_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error discovering sitemap for {base_url}: {str(e)}")
            return None

    async def fetch_urls_from_sitemap(self, sitemap_url: str, filter_pattern: str = "") -> List[str]:
        """Fetch all URLs from a sitemap with optional filtering."""
        try:
            logger.info(f"Fetching URLs from sitemap: {sitemap_url}")
            
            # Wait for rate limiter
            await self.url_rate_limiter.wait()
            
            # Use requests for synchronous operation when async is not available
            response = requests.get(sitemap_url, headers=self.browser_headers, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ElementTree.fromstring(response.content)
            
            # Extract all URLs from the sitemap
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            all_urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
            
            # Apply filter if specified
            if filter_pattern:
                filtered_urls = [url for url in all_urls if re.search(filter_pattern, url, re.IGNORECASE)]
                logger.info(f"Found {len(filtered_urls)} URLs (filtered from {len(all_urls)} total)")
                return filtered_urls
            else:
                logger.info(f"Found {len(all_urls)} URLs in sitemap")
                return all_urls
            
        except Exception as e:
            logger.error(f"Error fetching sitemap {sitemap_url}: {str(e)}")
            # Fall back to basic URL list
            return []

async def main():
    """Main function to run the semantic URL ingestion process."""
    ingester = None
    try:
        logger.info("Starting semantic URL ingestion process...")
        
        # Create the semantic ingester
        ingester = SemanticURLIngester()
        
        # Process climate report URLs with enhanced semantic extraction
        await ingester.process_climate_reports()
        
        # Process company websites using sitemaps
        await ingester.process_companies_with_sitemaps()
        
        logger.info("Semantic URL ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during semantic URL ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        # Clean up resources
        if ingester:
            await ingester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 