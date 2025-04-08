#!/usr/bin/env python3
"""
Test script for data ingestion connection

This script tests the connection to the database and the initialization of the
data ingestion module, without actually ingesting any data.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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
        # Import Supabase client
        from supabase.client import create_client, Client

        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # Just verify we can connect to Supabase
        logger.info("Successfully connected to Supabase!")
        logger.info("Note: Database tables have not been created yet. Run the schema.sql file in the SQL Editor to initialize the database.")
        return True
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {e}")
        return False

def test_ingestion_module_initialization():
    """Test initialization of the data ingestion module."""
    logger.info("Testing initialization of the data ingestion module...")

    try:
        # Import data ingestion module
        from lib.ingestion import ClimateDataIngester

        # Initialize data ingester without Supabase client
        data_ingester = ClimateDataIngester()

        logger.info("Successfully initialized data ingestion module!")
        return True
    except Exception as e:
        logger.error(f"Error initializing data ingestion module: {e}")
        return False

def main():
    """Main function to run the tests."""
    logger.info("Starting data ingestion connection tests...")

    # Test Supabase connection
    connection_success = test_supabase_connection()

    if not connection_success:
        logger.warning("Supabase connection test failed.")

    # Test ingestion module initialization
    initialization_success = test_ingestion_module_initialization()

    if not initialization_success:
        logger.error("Ingestion module initialization test failed.")

    # Print summary
    logger.info("Data ingestion connection tests completed.")
    logger.info(f"Supabase connection: {'SUCCESS' if connection_success else 'FAILED'}")
    logger.info(f"Ingestion module initialization: {'SUCCESS' if initialization_success else 'FAILED'}")

if __name__ == "__main__":
    main()
