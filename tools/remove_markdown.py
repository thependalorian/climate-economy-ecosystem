#!/usr/bin/env python3

import os
import sys
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))

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

def delete_markdown_records():
    """Delete records related to the supabase-ssr-integration.md file from climate_memories table."""
    try:
        logger.info("Starting deletion of markdown records from climate_memories table...")
        
        # Find all records with the supabase-ssr-integration.md source
        source_pattern = "%supabase-ssr-integration.md%"
        
        # URL-encode the pattern
        encoded_pattern = requests.utils.quote(source_pattern)
        
        # Query to find records
        query_url = f"{SUPABASE_URL}/rest/v1/climate_memories?select=id,metadata&metadata->>source=like.{encoded_pattern}"
        
        response = requests.get(
            query_url,
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code != 200:
            logger.error(f"Error querying records: {response.status_code} {response.text}")
            return False
        
        records = response.json()
        logger.info(f"Found {len(records)} records to delete")
        
        if not records:
            logger.info("No matching records found")
            return True
        
        # Delete each record
        for record in records:
            record_id = record.get('id')
            if not record_id:
                continue
                
            delete_url = f"{SUPABASE_URL}/rest/v1/climate_memories?id=eq.{record_id}"
            
            delete_response = requests.delete(
                delete_url,
                headers=SUPABASE_HEADERS
            )
            
            if delete_response.status_code in [200, 204]:
                logger.info(f"Successfully deleted record {record_id}")
            else:
                logger.error(f"Failed to delete record {record_id}: {delete_response.status_code}")
        
        logger.info("Deletion completed")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting markdown records: {str(e)}")
        return False

if __name__ == "__main__":
    if delete_markdown_records():
        logger.info("Successfully removed markdown records from database")
    else:
        logger.error("Failed to remove markdown records from database")
        sys.exit(1) 