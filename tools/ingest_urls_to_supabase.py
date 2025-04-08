#!/usr/bin/env python3
"""
URL Structure Ingestion to Supabase - Focused script to ingest tiered URL data into Supabase
"""

import os
import sys
import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime, timezone
from openai import OpenAI

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the StrategicURLIngester class
from strategic_url_ingestion import StrategicURLIngester, RateLimiter, logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('url_ingestion.log')
    ]
)

class StructuredURLIngester:
    """Ingests URLs from structured tiers into Supabase database."""
    
    def __init__(self):
        """Initialize the URL ingester with the core strategic ingester."""
        self.ingester = StrategicURLIngester()
        
        # Track URLs that have been processed
        self.processed_urls: Set[str] = set()
        
        # Stats tracking
        self.tier1_success = 0
        self.tier1_failed = 0
        self.tier2_success = 0
        self.tier2_failed = 0
        self.tier3_success = 0
        self.tier3_failed = 0
        
    async def process_url_list(self, urls: List[str], tier: int, org_type: str = None) -> int:
        """Process a list of URLs with the specified tier and organization type."""
        success_count = 0
        
        for url in urls:
            if url in self.processed_urls:
                logger.info(f"URL {url} already processed, skipping")
                continue
                
            # Map organization type based on URL domain
            company_name = None
            if "tps-energy.com" in url:
                company_name = "TPS Energy"
            elif "ulem.org" in url:
                company_name = "ULEM"
            elif "myheadlamp.com" in url:
                company_name = "MyHeadlamp"
            elif "africanbn.org" in url:
                company_name = "AfricanBN"
            elif "franklincummings.edu" in url:
                company_name = "FranklinCummings"
            elif "mass.gov/masshire" in url:
                company_name = "MassHire"
            elif "masscec.com" in url:
                company_name = "MassCEC"
            elif "joinact.org" in url:
                company_name = "ACT"
            elif "greentownlabs.com" in url:
                company_name = "Greentown Labs"
            
            logger.info(f"TIER {tier}: Processing URL: {url} ({company_name or 'Unknown'})")
            
            success, additional_urls = await self.ingester.process_url(url, company_name, tier)
            
            self.processed_urls.add(url)
            
            if success:
                success_count += 1
                if tier == 1:
                    self.tier1_success += 1
                elif tier == 2:
                    self.tier2_success += 1
                elif tier == 3:
                    self.tier3_success += 1
            else:
                if tier == 1:
                    self.tier1_failed += 1
                elif tier == 2:
                    self.tier2_failed += 1
                elif tier == 3:
                    self.tier3_failed += 1
            
            # Wait between requests
            await asyncio.sleep(2)
        
        return success_count
    
    async def process_tiered_structure(self) -> bool:
        """Process all URLs in the tiered structure."""
        logger.info("Starting URL structure ingestion to Supabase")
        
        # Process Primary Tier (Tier 1)
        logger.info("Processing Primary Tier URLs")
        primary_urls = URL_STRUCTURE["Tiered_Content_Approach"]["Primary_Tier"]
        primary_success = await self.process_url_list(primary_urls, 1)
        logger.info(f"Completed Primary Tier: {primary_success}/{len(primary_urls)} successful")
        
        # Process Secondary Tier (Tier 2)
        logger.info("Processing Secondary Tier URLs")
        secondary_urls = URL_STRUCTURE["Tiered_Content_Approach"]["Secondary_Tier"]
        secondary_success = await self.process_url_list(secondary_urls, 2)
        logger.info(f"Completed Secondary Tier: {secondary_success}/{len(secondary_urls)} successful")
        
        # Process Organization-Specific URLs
        for org_type, urls in URL_STRUCTURE["Organization_Specific_Strategies"].items():
            logger.info(f"Processing {org_type} URLs")
            org_success = await self.process_url_list(urls, 1, org_type)
            logger.info(f"Completed {org_type}: {org_success}/{len(urls)} successful")
        
        # Process Special Content Types
        for content_type, urls in URL_STRUCTURE["Content_Extraction_Methods"].items():
            logger.info(f"Processing {content_type} URLs")
            content_success = await self.process_url_list(urls, 1)
            logger.info(f"Completed {content_type}: {content_success}/{len(urls)} successful")
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print a summary of the ingestion results."""
        logger.info("=" * 50)
        logger.info("URL INGESTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"PRIMARY TIER: {self.tier1_success} successful, {self.tier1_failed} failed")
        logger.info(f"SECONDARY TIER: {self.tier2_success} successful, {self.tier2_failed} failed")
        logger.info(f"TERTIARY TIER: {self.tier3_success} successful, {self.tier3_failed} failed")
        logger.info(f"TOTAL PROCESSED: {len(self.processed_urls)} URLs")
        logger.info(f"TOTAL SUCCESS RATE: {(self.tier1_success + self.tier2_success + self.tier3_success) / len(self.processed_urls) * 100:.2f}%")
        logger.info("=" * 50)

async def main():
    """Main entry point."""
    ingester = StructuredURLIngester()
    await ingester.process_tiered_structure()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        sys.exit(1) 