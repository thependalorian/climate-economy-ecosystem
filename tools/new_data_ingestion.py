#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))
from constants import CLIMATE_REPORT_RESOURCES

# Import our database adapter
from climate_database import ClimateDatabase

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

class DataIngester:
    """Climate Economy Ecosystem data ingester."""
    
    def __init__(self):
        """Initialize the data ingester."""
        # Initialize database
        self.db = ClimateDatabase()
        
        # Configuration for processing
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
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
    
    async def store_document_chunks(self, content: str, metadata: Dict) -> int:
        """Store document chunks in the database.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Number of chunks successfully stored
        """
        # Split document into chunks
        chunks = self.smart_chunker(content)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        # Store each chunk
        success_count = 0
        for i, chunk in enumerate(chunks):
            # Create memory data
            memory_data = {
                'content': chunk,
                'metadata': metadata,
                'source_type': 'pdf',
                'url': str(metadata.get('source', '')),
                'title': metadata.get('file_name', ''),
                'chunk_index': i,
                'total_chunks': len(chunks)
            }
            
            # Add embedding
            embedding = await self.db.get_embedding(chunk)
            if embedding:
                memory_data['embedding'] = embedding
            
            # Store memory
            record_id = await self.db.store_climate_memory(memory_data)
            if record_id:
                success_count += 1
        
        return success_count
    
    async def process_documents_directory(self, directory: str) -> None:
        """Process all documents in a directory."""
        docs_dir = Path(directory)
        if not docs_dir.exists():
            logger.warning(f"Directory {directory} does not exist")
            return

        # Find all PDF files
        pdf_files = []
        for file_path in docs_dir.glob('**/*.pdf'):
            if file_path.is_file():
                pdf_files.append(file_path)
        
        logger.info(f"Found {len(pdf_files)} PDF documents to process")
        
        # Process each file
        for file_path in pdf_files:
            logger.info(f"Processing document: {file_path}")
            
            # Process the document
            result = await self.process_pdf(str(file_path))
            if not result:
                logger.error(f"Failed to process document: {file_path}")
                continue
                
            # Store document chunks
            metadata = {
                **result['metadata'],
                'source': str(file_path)
            }
            
            success_count = await self.store_document_chunks(result['content'], metadata)
            logger.info(f"Successfully stored {success_count} chunks from {file_path}")
    
    async def ingest_reports(self) -> None:
        """Ingest climate report PDFs."""
        logger.info("Ingesting climate reports...")
        await self.process_documents_directory(str(Path(__file__).parent.parent / 'docs'))
    
    async def test_search(self) -> None:
        """Test the search functionality."""
        logger.info("Testing search functionality...")
        
        test_queries = [
            "clean energy jobs in Massachusetts",
            "offshore wind workforce development",
            "heat pump installation training",
            "career pathways for environmental justice communities"
        ]
        
        for query in test_queries:
            logger.info(f"Searching for: {query}")
            results = await self.db.search_memories(query, 3)
            logger.info(f"Found {len(results)} results")
            
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}: {result.get('title', 'No title')} - "
                            f"Similarity: {result.get('similarity', 0):.2f}")
                
                # Show snippet of content
                content = result.get('content', '')
                if content:
                    snippet = content[:150] + "..." if len(content) > 150 else content
                    logger.info(f"Snippet: {snippet}")

async def main() -> None:
    """Main entry point."""
    try:
        logger.info("Starting climate economy ecosystem data ingestion...")
        
        ingester = DataIngester()
        
        # Ingest climate reports
        await ingester.ingest_reports()
        
        # Test search functionality
        await ingester.test_search()
        
        logger.info("Data ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 