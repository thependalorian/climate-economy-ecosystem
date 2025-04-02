#!/usr/bin/env python3
"""
Unified URL Ingestion System for Climate Economy Ecosystem
Consolidates functionality from multiple ingestion scripts into a single, efficient implementation.
"""

import os
import sys
import asyncio
import logging
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
import tempfile
import urllib.request

import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Constants and Configuration
CLIMATE_KEYWORDS = [
    "clean energy", "renewable energy", "climate tech", "sustainability",
    "climate economy", "green jobs", "carbon reduction", "net zero",
    "climate innovation", "solar", "wind power", "energy efficiency"
]

ORGANIZATION_TYPES = {
    "government": ["MassCEC", "MassHire"],
    "education": ["FranklinCummings"],
    "innovation": ["Greentown Labs", "ACT"],
    "service": ["TPS Energy", "ULEM", "MyHeadlamp", "AfricanBN"]
}

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
    sys.exit(1)

# Initialize base headers
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

SYSTEM_USER_ID = "system"

class RateLimiter:
    """Rate limiter for API calls."""
    
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

class UnifiedURLIngester:
    """Unified URL ingestion system combining best practices from all implementations."""
    
    def __init__(self):
        """Initialize the unified URL ingester."""
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize rate limiters
        self.url_rate_limiter = RateLimiter(0.5)  # 1 request per 2 seconds
        self.supabase_rate_limiter = RateLimiter(2.0)  # 2 requests per second
        
        # Configuration
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
        
        # Tracking
        self.processed_urls: Set[str] = set()
        self.success_count = 0
        self.failed_count = 0
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def smart_chunker(self, text: str) -> List[str]:
        """Split text into chunks intelligently, preserving context."""
        # Enforce maximum content size limit
        MAX_CONTENT_SIZE = 200000  # ~200KB max content size
        if len(text) > MAX_CONTENT_SIZE:
            logger.warning(f"Content too large ({len(text)} chars), truncating")
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
            if i + 1 < len(segments):
                segment += segments[i + 1]
                
            if current_length + len(segment) > self.chunk_size and current_chunk:
                chunks.append(''.join(current_chunk).strip())
                overlap_start = max(0, len(''.join(current_chunk)) - self.chunk_overlap)
                current_chunk = [''.join(current_chunk)[overlap_start:]]
                current_length = len(current_chunk[0])
            
            current_chunk.append(segment)
            current_length += len(segment)
        
        if current_chunk:
            chunks.append(''.join(current_chunk).strip())
        
        # Limit chunks
        MAX_CHUNKS = 20
        if len(chunks) > MAX_CHUNKS:
            logger.warning(f"Too many chunks ({len(chunks)}), limiting to {MAX_CHUNKS}")
            chunks = chunks[:MAX_CHUNKS]
            
        return chunks
    
    def extract_structured_content(self, element) -> str:
        """Extract content while preserving structure."""
        if not element:
            return ""
        
        content = []
        
        for child in element.find_all(recursive=False):
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(child.name[1])
                heading_text = child.get_text(strip=True)
                content.append(f"\n{'#' * level} {heading_text}\n")
            
            elif child.name == 'p':
                para_text = child.get_text(strip=True)
                if para_text:
                    content.append(f"{para_text}\n\n")
            
            elif child.name in ['ul', 'ol']:
                list_items = []
                for li in child.find_all('li', recursive=True):
                    li_text = li.get_text(strip=True)
                    prefix = '- ' if child.name == 'ul' else f"{len(list_items) + 1}. "
                    list_items.append(f"{prefix}{li_text}")
                if list_items:
                    content.append('\n' + '\n'.join(list_items) + '\n\n')
            
            elif child.name in ['div', 'section', 'article', 'main']:
                nested_content = self.extract_structured_content(child)
                if nested_content:
                    content.append(nested_content)
            
            elif child.name == 'a':
                link_text = child.get_text(strip=True)
                link_url = child.get('href', '')
                if link_text and link_url:
                    content.append(f"[{link_text}]({link_url}) ")
        
        if not content and element.get_text(strip=True):
            return element.get_text(separator='\n', strip=True)
        
        return '\n'.join(content)
    
    async def memory_exists(self, url: str, chunk_index: Optional[int] = None) -> bool:
        """Check if a memory already exists in the database."""
        try:
            await self.supabase_rate_limiter.wait()
            
            metadata_filter = f"metadata->>'url'=eq.{url}"
            if chunk_index is not None:
                metadata_filter += f"&metadata->>'chunk_index'=eq.{chunk_index}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SUPABASE_URL}/rest/v1/climate_memories?select=id&{metadata_filter}",
                    headers=SUPABASE_HEADERS
                )
            
            return response.status_code == 200 and len(response.json()) > 0
            
        except Exception as e:
            logger.warning(f"Error checking memory existence: {str(e)}")
            return False
    
    async def store_memory(self, content: str, metadata: Dict) -> bool:
        """Store a memory in the database."""
        try:
            await self.supabase_rate_limiter.wait()
            
            if not content or len(content.strip()) < 50:
                logger.warning(f"Content too short from {metadata.get('url', 'unknown')}")
                return False
            
            if await self.memory_exists(metadata['url'], metadata.get('chunk_index')):
                logger.info(f"Memory already exists for {metadata['url']}")
                return True
            
            memory_data = {
                'content': content,
                'user_id': SYSTEM_USER_ID,
                'metadata': metadata
            }
            
            embedding = await self.get_embedding(content)
            if embedding:
                memory_data['embedding'] = embedding
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/climate_memories",
                    headers=SUPABASE_HEADERS,
                    json=memory_data
                )
            
            success = response.status_code == 201
            if success:
                logger.info(f"Successfully stored memory from {metadata.get('url', 'unknown')}")
            else:
                logger.error(f"Failed to store memory: {response.status_code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return False
    
    async def process_webpage(self, url: str, tier: int = 1) -> Tuple[bool, List[str]]:
        """Process a webpage and extract its content."""
        try:
            await self.url_rate_limiter.wait()
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self.browser_headers)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url.split('/')[-1]
            
            # Find main content
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_='content') or 
                soup.find('div', id='content') or
                soup
            )
            
            # Extract content
            content = self.extract_structured_content(main_content)
            
            # Find additional URLs to crawl
            additional_urls = []
            if tier < 3:  # Only collect URLs for tier 1 and 2
                domain = urlparse(url).netloc
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/'):
                        href = urljoin(url, href)
                    if urlparse(href).netloc == domain:
                        additional_urls.append(href)
            
            # Create chunks
            chunks = self.smart_chunker(content)
            
            # Store chunks
            success_count = 0
            for i, chunk in enumerate(chunks):
                metadata = {
                    'url': url,
                    'title': title,
                    'tier': tier,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'indexed_at': datetime.now(timezone.utc).isoformat()
                }
                
                if await self.store_memory(chunk, metadata):
                    success_count += 1
            
            success = success_count > 0
            if success:
                self.success_count += 1
                logger.info(f"Successfully processed {url}")
            else:
                self.failed_count += 1
                logger.error(f"Failed to process {url}")
            
            return success, list(set(additional_urls))
            
        except Exception as e:
            logger.error(f"Error processing webpage {url}: {str(e)}")
            self.failed_count += 1
            return False, []
    
    async def process_url_list(self, urls: List[str], tier: int) -> int:
        """Process a list of URLs."""
        success_count = 0
        additional_urls = set()
        
        for url in urls:
            if url in self.processed_urls:
                continue
            
            self.processed_urls.add(url)
            success, new_urls = await self.process_webpage(url, tier)
            
            if success:
                success_count += 1
                additional_urls.update(new_urls)
            
            await asyncio.sleep(2)  # Rate limiting between URLs
        
        # Process additional URLs at next tier
        if tier < 3 and additional_urls:
            next_tier_urls = [url for url in additional_urls if url not in self.processed_urls]
            if next_tier_urls:
                logger.info(f"Processing {len(next_tier_urls)} discovered URLs at tier {tier + 1}")
                additional_success = await self.process_url_list(next_tier_urls, tier + 1)
                success_count += additional_success
        
        return success_count
    
    def print_summary(self):
        """Print ingestion summary."""
        logger.info("=" * 50)
        logger.info("URL INGESTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total URLs Processed: {len(self.processed_urls)}")
        logger.info(f"Successful: {self.success_count}")
        logger.info(f"Failed: {self.failed_count}")
        success_rate = (self.success_count / len(self.processed_urls) * 100) if self.processed_urls else 0
        logger.info(f"Success Rate: {success_rate:.2f}%")
        logger.info("=" * 50)

async def main():
    """Main entry point."""
    try:
        ingester = UnifiedURLIngester()
        
        # Test with a single URL first
        test_url = "https://www.masscec.com/"
        logger.info(f"Testing with single URL: {test_url}")
        
        success_count = await ingester.process_url_list([test_url], tier=1)
        ingester.print_summary()
        
        logger.info(f"Processed {success_count} URLs successfully")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 