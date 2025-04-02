#!/usr/bin/env python3
"""
Download required climate reports for ingestion into the Massachusetts Climate Economy Assistant

Usage:
    python download_reports.py

This script downloads the required climate reports from their sources if they
are not already present in the reports directory.
"""

import os
import sys
import asyncio
import logging
from urllib.parse import urlparse
import httpx

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import CLIMATE_REPORT_RESOURCES, REQUIRED_REPORTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

REPORTS_DIR = "reports"

async def download_report(url, filename):
    """Download a report from a URL to a local file"""
    filepath = os.path.join(REPORTS_DIR, filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        logger.info(f"Report already exists: {filepath}")
        return True
    
    try:
        logger.info(f"Downloading report from {url} to {filepath}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                logger.error(f"Failed to download {url}: HTTP {response.status_code}")
                return False
            
            # Save the file
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded {filename}")
            return True
            
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

async def download_all_reports():
    """Download all required reports"""
    # Create reports directory if it doesn't exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Define report URLs and filenames
    reports = {
        "https://www.masscec.com/download/7/asset/Powering_the_Future_A_Massachusetts_Clean_Energy_Workforce_Needs_Assessment_Final.pdf": 
            "Powering_the_Future_A_Massachusetts_Clean_Energy_Workforce_Needs_Assessment_Final.pdf",
        "https://www.necec.org/download/11/asset/NECEC_2023_Annual_Report.pdf":
            "NECEC_2023_Annual_Report.pdf"
    }
    
    # Download each report
    tasks = []
    for url, filename in reports.items():
        task = download_report(url, filename)
        tasks.append(task)
    
    # Wait for all downloads to complete
    results = await asyncio.gather(*tasks)
    
    # Check if all downloads were successful
    if all(results):
        logger.info("All reports downloaded successfully")
        return True
    else:
        logger.warning("Some reports failed to download")
        return False

if __name__ == "__main__":
    asyncio.run(download_all_reports()) 