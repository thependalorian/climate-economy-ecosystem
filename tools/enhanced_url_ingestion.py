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
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree
import tempfile
import urllib.request
from PyPDF2 import PdfReader
from openai import OpenAI
from bs4 import BeautifulSoup

# Import crawl4ai components
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
    from crawl4ai.deep_crawling.filters import FilterChain, ContentTypeFilter, SEOFilter, DomainFilter
    from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("crawl4ai not available. Install with: pip install crawl4ai")

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))
from constants import (
    CLIMATE_REPORT_RESOURCES,
    ACT_COMPANIES,
    EDUCATION_RESOURCES,
    MASSACHUSETTS_CLIMATE_RESOURCES,
    CLEAN_ENERGY_SECTORS,
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
        logging.FileHandler('enhanced_url_ingestion.log')
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

class EnhancedURLIngester:
    """Enhanced Climate Economy Ecosystem URL ingester with crawl4ai support."""
    
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
        
        # For crawl4ai - browser management
        self.active_crawlers = set()
        self.crawling_tasks = set()
        self.crawler_semaphore = asyncio.Semaphore(2)  # Max parallel crawlers
        self.should_exit = False
        
        # Set up browser config if crawl4ai is available
        if CRAWL4AI_AVAILABLE:
            self.browser_config = BrowserConfig(
                headless=True,
                ignore_https_errors=True,
                default_timeout=30000,  # 30 seconds
                user_agent=self.browser_headers['User-Agent'],
                viewport_width=1280,
                viewport_height=800
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
        
        # Limit chunks for URL content to avoid excessive processing
        MAX_CHUNKS = 20  # Limit for URL content to be more reasonable
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
    
    async def fetch_urls_from_sitemap(self, sitemap_url: str, filter_pattern: str = "") -> List[str]:
        """Fetch all URLs from a sitemap with optional filtering."""
        try:
            logger.info(f"Fetching URLs from sitemap: {sitemap_url}")
            
            async with requests.sessions.AsyncSession() as session:
                async with session.get(sitemap_url, timeout=30) as response:
                    response.raise_for_status()
                    content = await response.read()
                    
                    # Parse XML
                    root = ElementTree.fromstring(content)
                    
                    # Extract all URLs from the sitemap
                    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    all_urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
                    
                    # Apply filter if specified
                    if filter_pattern:
                        filtered_urls = [url for url in all_urls if filter_pattern in url]
                        logger.info(f"Found {len(filtered_urls)} URLs (filtered from {len(all_urls)} total)")
                        return filtered_urls
                    else:
                        logger.info(f"Found {len(all_urls)} URLs in sitemap")
                        return all_urls
                    
        except Exception as e:
            logger.error(f"Error fetching sitemap {sitemap_url}: {str(e)}")
            # Fall back to basic URL list
            return []
    
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
    
    async def process_webpage_with_requests(self, url: str) -> Optional[Dict]:
        """Process a webpage using requests and BeautifulSoup (fallback method)."""
        try:
            logger.info(f"Processing webpage with requests: {url}")
            
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
            
            # Extract all text with structure preserved
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup
            text = self.extract_structured_content(main_content)
            
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
    
    async def process_webpage_with_crawl4ai(self, url: str) -> Optional[Dict]:
        """Process a webpage using crawl4ai for better JavaScript rendering."""
        if not CRAWL4AI_AVAILABLE:
            logger.warning("crawl4ai not available, falling back to requests method")
            return await self.process_webpage_with_requests(url)
            
        # Acquire semaphore to limit concurrency
        async with self.crawler_semaphore:
            crawler = None
            try:
                logger.info(f"Processing webpage with crawl4ai: {url}")
                
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
                
                # Configure crawler run
                crawler_config = CrawlerRunConfig(
                    page_timeout=60000,  # 60 seconds
                    wait_for_network_idle=True,
                    wait_for_timeout=5000,  # 5 seconds after load
                    extract_markdown=True,  # Enable markdown extraction
                    markdown_generator=DefaultMarkdownGenerator()  # Use default markdown generator
                )
                
                # Crawl the page
                result = None
                try:
                    crawl_task = asyncio.create_task(crawler.arun(url=url, config=crawler_config))
                    self.crawling_tasks.add(crawl_task)
                    result = await asyncio.wait_for(crawl_task, timeout=90)  # 90 second timeout
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
                
                # Extract content
                content = None
                try:
                    # Try different content extraction methods
                    if (hasattr(result, 'markdown_v2') and result.markdown_v2 is not None and 
                        hasattr(result.markdown_v2, 'raw_markdown') and result.markdown_v2.raw_markdown):
                        content = result.markdown_v2.raw_markdown
                    elif hasattr(result, 'markdown') and result.markdown:
                        content = result.markdown
                    elif hasattr(result, 'html') and result.html:
                        # Convert HTML to markdown as fallback
                        soup = BeautifulSoup(result.html, 'html.parser')
                        content = soup.get_text(separator='\n', strip=True)
                    else:
                        logger.warning(f"No content found in result for {url}")
                        return None
                except Exception as e:
                    logger.error(f"Error extracting content from {url}: {str(e)}")
                    return None
                
                # Extract title from the first heading or URL
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
    
    async def process_url(self, url: str, source_type: str = 'report', organization: str = None) -> bool:
        """Process a URL (either webpage or PDF)."""
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
                # Process PDF
                result = await self.download_and_process_pdf(url)
            else:
                # Try crawl4ai first, fallback to requests if needed
                result = await self.process_webpage_with_crawl4ai(url) or await self.process_webpage_with_requests(url)
            
            # Mark as processed
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
            company_url = company.get('url', '')
            company_sector = company.get('sector', '')
            company_url_count = 0
            
            logger.info(f"Processing resources for company: {company_name}")
            
            # Try sitemap-based crawling first if main URL is available
            if company_url:
                # First, store the main company page
                logger.info(f"Processing main company page: {company_url}")
                if await self.process_url(company_url, 'company_resource', company_name):
                    company_url_count += 1
                
                # Try to discover and process sitemap
                sitemap_url = await self.auto_discover_sitemap(company_url)
                if sitemap_url:
                    # For sitemap-based crawling, limit to key pages
                    sitemap_success = await self.process_sitemap_urls(
                        sitemap_url,
                        filter_pattern="/about|/jobs|/careers|/services",
                        source_type='company_resource',
                        organization=company_name
                    )
                    company_url_count += sitemap_success
                    logger.info(f"Processed {sitemap_success} URLs from sitemap for {company_name}")
            
            # Process each resource URL individually
            for resource_url in company_resources:
                # Skip non-HTTP URLs
                if not resource_url.startswith('http'):
                    continue
                
                logger.info(f"Processing resource: {resource_url}")
                
                # Skip if it's the main company URL (already processed)
                if resource_url == company_url:
                    continue
                
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
            
            # Process company data directly
            await self.process_company_data(company)
            
            # Mark company as indexed
            if company_url_count > 0:
                mark_company_as_indexed(company_name)
                
            # Save progress after each company
            save_company_index_status()
        
        logger.info(f"Successfully processed {success_count} company resource URLs")
        return success_count
    
    async def process_company_data(self, company: Dict) -> bool:
        """Directly ingest company information from constants.py."""
        try:
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
                'url': company.get('url', ''),  # Include URL as identifier
                'indexed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Store the company data
            if await self.store_memory(content, SYSTEM_USER_ID, metadata):
                logger.info(f"Successfully stored company data for: {company_name}")
                return True
            else:
                logger.error(f"Failed to store company data for: {company_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing company data: {str(e)}")
            return False
    
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
    
    async def process_sectors(self) -> int:
        """Process sector information from constants."""
        logger.info("Processing sector data...")
        success_count = 0
        
        for sector in CLEAN_ENERGY_SECTORS:
            # For each sector, create a description
            content = f"# {sector}\n\n"
            content += f"This is a key sector in the Massachusetts clean energy economy.\n\n"
            
            # Match companies in this sector
            sector_companies = [company['name'] for company in ACT_COMPANIES if company.get('sector') == sector]
            if sector_companies:
                content += f"## Companies in this sector\n\n"
                for company in sector_companies:
                    content += f"- {company}\n"
                content += "\n"
            
            metadata = {
                'source_type': 'sector_data',
                'sector': sector,
                'indexed_at': datetime.now(timezone.utc).isoformat()
            }
            
            if await self.store_memory(content, SYSTEM_USER_ID, metadata):
                success_count += 1
                logger.info(f"Successfully stored sector data for: {sector}")
                
        logger.info(f"Successfully processed {success_count}/{len(CLEAN_ENERGY_SECTORS)} sectors")
        return success_count
    
    async def cleanup(self):
        """Clean up resources before exiting."""
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

async def main() -> None:
    """Main function to run the URL ingestion process."""
    ingester = None
    try:
        logger.info("Starting enhanced URL ingestion process...")
        
        # Create ingester
        ingester = EnhancedURLIngester()
        
        # Process company data
        await ingester.process_company_data({"name": "Massachusetts Clean Energy Center", "description": "State economic development agency dedicated to clean energy", "sector": "Economic Development"})
        
        # Process climate report URLs
        await ingester.process_climate_reports()
        
        # Process company resources
        await ingester.process_company_resources()
        
        # Process education resources
        await ingester.process_education_resources()
        
        # Process sectors
        await ingester.process_sectors()
        
        logger.info("URL ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during URL ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        # Clean up resources
        if ingester:
            await ingester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 