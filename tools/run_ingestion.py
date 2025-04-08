#!/usr/bin/env python3
"""
Script to run the data ingestion process for the Climate Economy Ecosystem.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.data_ingestion import main as ingest_data

async def main():
    """Main function to run the data ingestion process."""
    try:
        logger.info("Starting data ingestion process...")
        await ingest_data()
        logger.info("Data ingestion completed successfully!")
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 