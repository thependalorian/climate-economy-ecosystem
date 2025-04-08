#!/usr/bin/env python3
"""
Test script for database connection and retrieval functionality.
This script tests the connection to the database and the retrieval functionality
without running the actual ingestion process to avoid creating duplicates.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('connection_retrieval_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import necessary modules
try:
    from lib.retrieval.massachusetts_climate_retriever import MassachusettsClimateRetriever
    from supabase.client import create_client, Client
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def test_supabase_connection():
    """Test connection to Supabase."""
    logger.info("Testing connection to Supabase...")
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not found in environment variables.")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching a small amount of data
        response = supabase.table('profiles').select('id').limit(1).execute()
        
        if response.data is not None:
            logger.info("Successfully connected to Supabase!")
            return True
        else:
            logger.error("Failed to retrieve data from Supabase.")
            return False
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {e}")
        return False

def test_retrieval_functionality():
    """Test retrieval functionality."""
    logger.info("Testing retrieval functionality...")
    
    # Get OpenAI API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        logger.error("OpenAI API key not found in environment variables.")
        return False
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not found in environment variables.")
        return False
    
    try:
        # Initialize the retriever
        retriever = MassachusettsClimateRetriever(
            openai_api_key=openai_api_key,
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        
        # Test retrieval with a sample query
        query = "What are some clean energy job opportunities in Massachusetts?"
        results = retriever.retrieve(query, limit=3)
        
        if results:
            logger.info(f"Successfully retrieved {len(results)} documents!")
            logger.info(f"Sample result: {results[0][:200]}...")
            return True
        else:
            logger.warning("No documents retrieved. This could be normal if no relevant documents exist.")
            return True
    except Exception as e:
        logger.error(f"Error testing retrieval functionality: {e}")
        return False

def test_document_count():
    """Test counting documents in the database."""
    logger.info("Testing document count in the database...")
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not found in environment variables.")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Count documents in the documents table
        response = supabase.table('documents').select('id', count='exact').execute()
        
        if response.count is not None:
            logger.info(f"Document count: {response.count}")
            return True
        else:
            logger.error("Failed to count documents.")
            return False
    except Exception as e:
        logger.error(f"Error counting documents: {e}")
        return False

def main():
    """Main function to run the tests."""
    logger.info("Starting connection and retrieval tests...")
    
    # Test Supabase connection
    connection_success = test_supabase_connection()
    
    if not connection_success:
        logger.error("Supabase connection test failed. Exiting...")
        return
    
    # Test document count
    count_success = test_document_count()
    
    if not count_success:
        logger.warning("Document count test failed. Continuing...")
    
    # Test retrieval functionality
    retrieval_success = test_retrieval_functionality()
    
    if not retrieval_success:
        logger.error("Retrieval functionality test failed.")
    
    logger.info("Connection and retrieval tests completed.")

if __name__ == "__main__":
    main()
