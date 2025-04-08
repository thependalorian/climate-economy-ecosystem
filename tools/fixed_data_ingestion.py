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
from openai import OpenAI

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))
from constants import CLIMATE_REPORT_RESOURCES

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

class DataIngester:
    """Climate Economy Ecosystem data ingester."""
    
    def __init__(self):
        """Initialize the data ingester."""
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize rate limiter for Supabase calls
        self.rate_limiter = RateLimiter(2.0)  # 2 calls per second
        
        # Configuration for processing
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
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
        MAX_CHUNKS = 50
        if len(chunks) > MAX_CHUNKS:
            logger.warning(f"Too many chunks ({len(chunks)}), limiting to {MAX_CHUNKS}")
            chunks = chunks[:MAX_CHUNKS]
            
        return chunks
    
    async def memory_exists(self, source: str, chunk_index: Optional[int] = None) -> bool:
        """Check if a memory already exists in the database."""
        try:
            await self.rate_limiter.wait()
            
            # Build the query to search in metadata
            metadata_filter = f"metadata->>'source'=eq.{requests.utils.quote(source)}"
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
            await self.rate_limiter.wait()
            
            # Skip if content is too short
            if not content or len(content.strip()) < 50:
                logger.warning(f"Content too short, skipping")
                return False
            
            # Check if memory already exists
            if 'source' in metadata:
                chunk_index = metadata.get('chunk_index')
                if await self.memory_exists(metadata['source'], chunk_index):
                    logger.info(f"Memory from {metadata['source']} already exists, skipping")
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
            await self.rate_limiter.wait()
            
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
    
    async def process_pdf(self, file_path: str) -> Optional[Dict]:
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
    
    async def process_documents_directory(self, directory: str) -> None:
        """Process all documents in a directory."""
        try:
            docs_dir = Path(directory)
            if not docs_dir.exists():
                logger.warning(f"Directory {directory} does not exist")
                return

            # Find all PDF files
            files_to_process = []
            for file_path in docs_dir.glob('**/*.pdf'):
                if file_path.is_file():
                    files_to_process.append(file_path)
            
            logger.info(f"Found {len(files_to_process)} documents to process")
            
            # Process files sequentially
            for file_path in files_to_process:
                logger.info(f"Processing document: {file_path}")
                
                # Process the document
                result = await self.process_pdf(str(file_path))
                
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
                            'chunk_index': i,
                            'total_chunks': len(chunks)
                        }
                        
                        # Store the chunk
                        if await self.store_memory(chunk, SYSTEM_USER_ID, chunk_metadata):
                            success_count += 1
                    
                    logger.info(f"Successfully stored {success_count}/{len(chunks)} chunks from {file_path}")
                else:
                    # Store single document
                    metadata = {
                        **result['metadata'],
                        'source': str(file_path)
                    }
                    
                    if await self.store_memory(content, SYSTEM_USER_ID, metadata):
                        logger.info(f"Successfully stored document: {file_path}")
                    else:
                        logger.error(f"Failed to store document: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing documents directory: {str(e)}")
            raise

async def main() -> None:
    """Main function to run the data ingestion process."""
    try:
        logger.info("Starting data ingestion process...")
        
        # Create ingester
        ingester = DataIngester()
        
        # Process documents
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