#!/usr/bin/env python3
"""
Data Ingestion Tool for Massachusetts Climate Economy Assistant

This script crawls and indexes content from company resources, climate reports,
and other educational content to build a knowledge base for the Climate Economy
Ecosystem Assistant.

Usage:
    python data_ingestion.py [--companies COMPANY1,COMPANY2,...] [--reports] [--force]

Options:
    --companies  Only process specified companies (comma-separated)
    --reports    Only process PDF reports
    --force      Force reindexing even if already indexed
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
import traceback
import time

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    ACT_COMPANIES, 
    CLIMATE_REPORT_RESOURCES, 
    REQUIRED_REPORTS,
    is_company_indexed,
    mark_company_as_indexed,
    get_unindexed_companies,
    save_company_index_status,
    load_company_index_status
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('climate_data_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    logger.error("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
    sys.exit(1)

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    logger.info("Successfully initialized Supabase client")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    sys.exit(1)

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@dataclass
class IngestionConfig:
    """Configuration for the data ingestion tool."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_concurrent_tasks: int = 5
    rate_limit_delay: float = 0.5  # seconds between requests
    supabase_rate_limit: float = 0.2  # seconds between Supabase calls
    page_timeout: int = 30  # seconds
    user_agent: str = "Massachusetts Climate Economy Assistant Indexer Bot (Contact: support@macleantech.org)"
    docs_dir: str = "docs"  # Updated to use docs directory

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
    """Indexes climate economy content from various sources."""
    
    def __init__(self, config: Optional[IngestionConfig] = None):
        """Initialize the ingester with configuration."""
        self.config = config or IngestionConfig()
        self.processed_urls: Set[str] = set()
        
        # Initialize rate limiters
        self.api_rate_limiter = RateLimiter(1.0/self.config.rate_limit_delay)
        self.supabase_rate_limiter = RateLimiter(1.0/self.config.supabase_rate_limit)
        
        # Create reports directory if it doesn't exist
        os.makedirs(self.config.docs_dir, exist_ok=True)
        
        # For graceful shutdown
        self.should_exit = False
        
        # Load tracking data
        load_company_index_status()
        
    def handle_shutdown_signal(self, sig=None, frame=None):
        """Handle shutdown signal gracefully."""
        logger.info("Shutdown signal received, cleaning up...")
        self.should_exit = True
        logger.info("Saving current progress...")
        save_company_index_status()

    def smart_chunker(self, text: str) -> List[str]:
        """Split text into chunks intelligently, trying to maintain context."""
        # Enforce maximum content size limit to prevent memory issues
        MAX_CONTENT_SIZE = 500000  # ~500KB max content size
        if len(text) > MAX_CONTENT_SIZE:
            logger.warning(f"Content too large ({len(text)} chars), truncating to {MAX_CONTENT_SIZE} chars")
            text = text[:MAX_CONTENT_SIZE]
        
        # Use LangChain's RecursiveCharacterTextSplitter for smart chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        # Enforce maximum number of chunks to prevent excessive processing
        MAX_CHUNKS = 50
        if len(chunks) > MAX_CHUNKS:
            logger.warning(f"Too many chunks ({len(chunks)}), limiting to {MAX_CHUNKS}")
            chunks = chunks[:MAX_CHUNKS]
        
        return chunks

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def store_document(self, source_type: str, text: str, metadata: Dict[str, Any]) -> bool:
        """Store a document in Supabase with retries."""
        try:
            # Wait for rate limiter before proceeding
            await self.supabase_rate_limiter.wait()
            
            # Validate required fields
            if not text or len(text.strip()) < 50:  # Skip very short content
                logger.warning(f"Content too short for {metadata.get('url', 'unknown')}, skipping")
                return False
                
            if not metadata.get("url") and not metadata.get("file_path"):
                logger.warning("Missing required 'url' or 'file_path' field in metadata, skipping")
                return False
                
            if not source_type:
                logger.warning("Missing required 'source_type', skipping")
                return False
            
            logger.info(f"Generating embedding for content from {metadata.get('url', metadata.get('file_path', 'unknown'))}")
            # Generate embedding using OpenAI
            embedding_list = await self.get_embedding(text)
            
            # Check if embedding is valid
            if not embedding_list or not isinstance(embedding_list, list):
                logger.warning(f"Invalid embedding generated for {metadata.get('url', 'unknown')}")
                return False
            
            # Parse URL for domain and path if available
            if metadata.get("url"):
                parsed_url = urlparse(metadata.get("url", ""))
                domain = parsed_url.netloc
                path = parsed_url.path
            else:
                domain = "local"
                path = metadata.get("file_path", "")
            
            # Create document with metadata and embedding
            document = {
                "content": text,
                "metadata": json.dumps(metadata),  # Convert metadata to JSON string
                "embedding": embedding_list,
                "source_type": source_type,
                "url": metadata.get("url", ""),
                "title": metadata.get("title", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "total_chunks": metadata.get("total_chunks", 1),
                "crawl_time": metadata.get("crawl_time", datetime.now(timezone.utc).isoformat()),
                "company": metadata.get("company", ""),
                "sector": metadata.get("sector", ""),
                "domain": domain,
                "path": path
            }
            
            logger.info(f"Storing document in Supabase: Source={metadata.get('url', metadata.get('file_path'))}, Title={metadata.get('title')}, Chunk={metadata.get('chunk_index')+1}/{metadata.get('total_chunks')}")
            
            try:
                # Insert into Supabase with better error handling
                await self.supabase_rate_limiter.wait()  # Wait again before actual API call
                result = supabase.table("climate_memories").insert(document).execute()
                if not result.data:
                    raise Exception("No data returned from Supabase insert")
                
                # Log success with more details
                logger.info(f"Successfully stored document: Source={metadata.get('url', metadata.get('file_path'))}, Title={metadata.get('title')}, Chunk={metadata.get('chunk_index')+1}/{metadata.get('total_chunks')}")
                return True
                
            except Exception as e:
                logger.error(f"Supabase insert error for {metadata.get('url', metadata.get('file_path', 'unknown'))}: {str(e)}")
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    logger.error(f"Response: {e.response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error storing document from {metadata.get('url', metadata.get('file_path', 'unknown'))}: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI with retries."""
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

    async def process_webpage(self, url: str, company_name: str, metadata: Dict[str, Any] = None) -> bool:
        """Process a single webpage for a company."""
        if url in self.processed_urls:
            logger.info(f"Skipping already processed URL: {url}")
            return False
            
        try:
            # Wait for rate limiter
            await self.api_rate_limiter.wait()
            
            # Fetch webpage content with reasonable timeout
            logger.info(f"Fetching content from {url}")
            async with httpx.AsyncClient(timeout=self.config.page_timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': self.config.user_agent
                })
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                    self.processed_urls.add(url)
                    return False
            
            # Parse HTML content
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract main content area (remove navigation, footers, etc.)
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else url.split('/')[-1]
            
            # Get text content with structure preserved
            text_content = self.extract_structured_content(main_content)
            
            if not text_content or len(text_content.strip()) < 100:
                logger.warning(f"Content too short or empty from {url}, only {len(text_content) if text_content else 0} chars")
                self.processed_urls.add(url)
                return False
            
            logger.info(f"Successfully extracted content from {url}")
            
            # Create chunks with metadata
            chunks = self.smart_chunker(text_content)
            logger.info(f"Created {len(chunks)} chunks from {url}")
            
            # Prepare standard metadata
            if metadata is None:
                metadata = {}
                
            base_metadata = {
                "url": url,
                "company": company_name,
                "title": title,
                "crawl_time": datetime.now(timezone.utc).isoformat(),
                **metadata
            }
            
            # Store each chunk
            success_count = 0
            for chunk_index, chunk in enumerate(chunks):
                chunk_metadata = {
                    **base_metadata,
                    "chunk_index": chunk_index,
                    "total_chunks": len(chunks),
                }
                
                success = await self.store_document(
                    source_type="company_resource",
                    text=chunk,
                    metadata=chunk_metadata
                )
                
                if success:
                    success_count += 1
            
            # Mark as processed
            self.processed_urls.add(url)
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing webpage {url}: {str(e)}")
            logger.error(traceback.format_exc())
            return False

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
                content.append('\n[Table content omitted]\n\n')
            
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
                    if link_url.startswith('/') or link_url.startswith('./'):
                        # Handle relative URLs
                        pass  # We don't need to expand them for our purposes
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

    async def process_company(self, company: Dict[str, Any]) -> Tuple[int, int]:
        """Process all resources for a company."""
        company_name = company["name"]
        resources = company.get("resources", [])
        
        if not resources:
            logger.warning(f"No resources found for company {company_name}")
            return 0, 0
            
        logger.info(f"Processing {len(resources)} resources for company {company_name}")
        
        # Track success/failure counts
        success_count = 0
        total_count = len(resources)
        
        # Process each resource
        for resource_url in resources:
            if self.should_exit:
                logger.info("Shutdown signal received, stopping processing")
                break
                
            # Process the webpage
            metadata = {
                "company": company_name,
                "focus_areas": company.get("focus_areas", []),
                "location": company.get("location", "Massachusetts")
            }
            
            success = await self.process_webpage(resource_url, company_name, metadata)
            if success:
                success_count += 1
                
        # Mark company as indexed if at least one resource was successful
        if success_count > 0:
            mark_company_as_indexed(company_name)
            await self.supabase_rate_limiter.wait()
            save_company_index_status()
            
        return success_count, total_count

    async def process_pdf_report(self, report_path: str) -> bool:
        """Process a PDF report and store its content."""
        try:
            if not os.path.exists(report_path):
                logger.warning(f"Report file not found: {report_path}")
                return False
                
            logger.info(f"Processing PDF report: {report_path}")
            
            # Extract filename and title
            filename = os.path.basename(report_path)
            title = filename.replace("_", " ").replace(".pdf", "")
            
            # Read PDF content
            pdf_text = ""
            pdf_reader = PdfReader(report_path)
            
            # Combine text from all pages
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n\n"
            
            if not pdf_text or len(pdf_text.strip()) < 100:
                logger.warning(f"PDF content too short or empty from {report_path}")
                return False
                
            logger.info(f"Successfully extracted {len(pdf_text)} chars from {report_path}")
            
            # Create chunks
            chunks = self.smart_chunker(pdf_text)
            logger.info(f"Created {len(chunks)} chunks from {report_path}")
            
            # Store each chunk
            success_count = 0
            for chunk_index, chunk in enumerate(chunks):
                if self.should_exit:
                    break
                    
                success = await self.store_document(
                    source_type="report",
                    text=chunk,
                    metadata={
                        "file_path": report_path,
                        "title": title,
                        "chunk_index": chunk_index,
                        "total_chunks": len(chunks),
                        "crawl_time": datetime.now(timezone.utc).isoformat(),
                    }
                )
                
                if success:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing PDF report {report_path}: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    async def is_resource_already_indexed(self, url: str) -> bool:
        """Check if a resource is already indexed in Supabase."""
        try:
            # Wait for rate limiter
            await self.supabase_rate_limiter.wait()
            
            # Check for URL in Supabase
            result = supabase.table("climate_memories").select("id").eq("url", url).limit(1).execute()
            exists = len(result.data) > 0
            
            if exists:
                logger.info(f"Resource {url} already indexed, skipping")
            
            return exists
            
        except Exception as e:
            logger.warning(f"Error checking if resource exists: {str(e)}")
            return False

    async def process_all_companies(self, company_names: Optional[List[str]] = None, force: bool = False):
        """Process all companies or a specific list."""
        total_processed = 0
        total_resources = 0
        
        # Get companies to process
        if company_names:
            companies = [c for c in ACT_COMPANIES if c["name"] in company_names]
        else:
            if not force:
                companies = get_unindexed_companies()
            else:
                companies = ACT_COMPANIES
        
        if not companies:
            logger.info("No unindexed companies found to process")
            return 0, 0
            
        logger.info(f"Processing {len(companies)} companies")
        
        # Process each company
        for company in companies:
            if self.should_exit:
                break
                
            company_name = company["name"]
            logger.info(f"\n=== Processing company: {company_name} ===")
            
            # Skip if already indexed and not forced
            if is_company_indexed(company_name) and not force:
                logger.info(f"Company {company_name} already indexed, skipping")
                continue
                
            # Process company resources
            success_count, total_count = await self.process_company(company)
            logger.info(f"Processed {success_count}/{total_count} resources for {company_name}")
            
            total_processed += success_count
            total_resources += total_count
        
        logger.info(f"\n=== Summary ===")
        logger.info(f"Successfully processed {total_processed}/{total_resources} resources")
        
        return total_processed, total_resources

    async def process_all_reports(self, force: bool = False):
        """Process all PDF reports."""
        total_success = 0
        total_reports = 0
        
        # List of reports to process
        reports_to_process = []
        
        # Check for local PDF files in reports directory
        for report_resource in CLIMATE_REPORT_RESOURCES:
            if not report_resource.startswith("http"):
                report_path = os.path.join(self.config.reports_dir, report_resource)
                if os.path.exists(report_path):
                    reports_to_process.append(report_path)
                else:
                    logger.warning(f"Report file not found: {report_path}")
        
        if not reports_to_process:
            logger.warning("No local PDF reports found to process")
            return 0, 0
            
        logger.info(f"Processing {len(reports_to_process)} PDF reports")
        
        # Process each report
        for report_path in reports_to_process:
            if self.should_exit:
                break
                
            logger.info(f"\n=== Processing report: {report_path} ===")
            total_reports += 1
            
            # Process report
            success = await self.process_pdf_report(report_path)
            if success:
                total_success += 1
        
        logger.info(f"\n=== PDF Report Summary ===")
        logger.info(f"Successfully processed {total_success}/{total_reports} reports")
        
        return total_success, total_reports

async def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Data Ingestion Tool for Massachusetts Climate Economy Assistant")
    parser.add_argument("--companies", help="Only process specified companies (comma-separated)")
    parser.add_argument("--reports", action="store_true", help="Only process PDF reports")
    parser.add_argument("--force", action="store_true", help="Force reindexing even if already indexed")
    
    args = parser.parse_args()
    
    # Initialize the ingester
    ingester = ClimateDataIngester()
    
    try:
        # Setup signal handlers for graceful shutdown
        import signal
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, ingester.handle_shutdown_signal)
        
        # Process according to arguments
        if args.companies:
            company_names = [name.strip() for name in args.companies.split(",")]
            await ingester.process_all_companies(company_names, args.force)
        elif args.reports:
            await ingester.process_all_reports(args.force)
        else:
            # Process both
            await ingester.process_all_companies(force=args.force)
            await ingester.process_all_reports(force=args.force)
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # Save progress
        save_company_index_status()
        logger.info("Data ingestion completed")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 