#!/usr/bin/env python3

import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def main():
    """Test Supabase connection using direct HTTP requests."""
    try:
        # Create headers for authentication
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Test querying the climate_memories table
        logger.info(f"Connecting to Supabase at {SUPABASE_URL}")
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/climate_memories?select=id",
            headers=headers
        )
        
        # Check response
        if response.status_code == 200:
            records = response.json()
            logger.info(f"Successfully connected to Supabase. Found {len(records)} records.")
            
            # Test insertion
            test_memory = {
                'content': 'Test memory for connection verification',
                'user_id': 'system',
                'metadata': {
                    'source': 'connection_test',
                    'type': 'test'
                }
            }
            
            insert_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/climate_memories",
                headers=headers,
                json=test_memory
            )
            
            if insert_response.status_code == 201:
                logger.info("Successfully inserted test record.")
                return True
            else:
                logger.error(f"Failed to insert test record: {insert_response.status_code} {insert_response.text}")
                return False
        else:
            logger.error(f"Failed to connect to Supabase: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    main() 