#!/usr/bin/env python3

import os
import logging
from pathlib import Path
from typing import Dict, Optional
from megaparse import MegaParse
from supabase import create_client, Client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('document_processing.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Initialize MegaParse
megaparse = MegaParse()

class DocumentProcessor:
    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.ensure_docs_directory()
    
    def ensure_docs_directory(self) -> None:
        """Ensure the docs directory exists."""
        if not self.docs_dir.exists():
            self.docs_dir.mkdir(parents=True)
            logger.info(f"Created docs directory: {self.docs_dir}")
    
    async def process_document(self, file_path: str) -> Optional[Dict]:
        """Process a single document using MegaParse."""
        try:
            # Process the document with MegaParse
            result = await megaparse.process_file(file_path)
            
            # Extract relevant information
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            
            return {
                'content': content,
                'metadata': metadata,
                'file_path': file_path
            }
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return None
    
    async def store_document(self, document_data: Dict) -> bool:
        """Store processed document in Supabase."""
        try:
            supabase.table('documents').insert({
                'file_path': document_data['file_path'],
                'content': document_data['content'],
                'metadata': document_data['metadata']
            }).execute()
            logger.info(f"Successfully stored document: {document_data['file_path']}")
            return True
        except Exception as e:
            logger.error(f"Error storing document {document_data['file_path']}: {str(e)}")
            return False
    
    async def process_directory(self) -> None:
        """Process all documents in the docs directory."""
        try:
            if not self.docs_dir.exists():
                logger.warning(f"Directory {self.docs_dir} does not exist")
                return

            # Process all files in the directory
            for file_path in self.docs_dir.glob('**/*'):
                if file_path.is_file():
                    logger.info(f"Processing document: {file_path}")
                    result = await self.process_document(str(file_path))
                    
                    if result:
                        await self.store_document(result)
                    
        except Exception as e:
            logger.error(f"Error processing documents directory: {str(e)}")
            raise

async def main():
    """Main function to run document processing."""
    try:
        processor = DocumentProcessor()
        await processor.process_directory()
        logger.info("Document processing completed successfully!")
    except Exception as e:
        logger.error(f"Error during document processing: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 