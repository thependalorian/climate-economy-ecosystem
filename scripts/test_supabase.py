#!/usr/bin/env python3
"""
Test script to verify Supabase setup and configuration.
"""

import os
import sys
import logging
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
    sys.exit(1)

# Initialize headers
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

async def test_supabase_connection():
    """Test connection to Supabase."""
    try:
        async with httpx.AsyncClient() as client:
            # Test database connection
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/climate_memories?select=count",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200:
                logger.info("✅ Successfully connected to Supabase")
                return True
            else:
                logger.error(f"❌ Failed to connect to Supabase: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Error connecting to Supabase: {str(e)}")
        return False

async def test_vector_extension():
    """Test if vector extension is enabled."""
    try:
        async with httpx.AsyncClient() as client:
            # Test vector extension
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/rpc/test_vector",
                headers=SUPABASE_HEADERS,
                json={
                    "v": [1.0] * 1536  # Test vector
                }
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Vector extension is working")
                return True
            else:
                logger.error(f"❌ Vector extension test failed: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Error testing vector extension: {str(e)}")
        return False

async def test_climate_memories_table():
    """Test climate_memories table structure."""
    try:
        async with httpx.AsyncClient() as client:
            # Get table info
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/climate_memories?select=id&limit=1",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200:
                logger.info("✅ climate_memories table exists and is accessible")
                return True
            else:
                logger.error(f"❌ Failed to access climate_memories table: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Error testing climate_memories table: {str(e)}")
        return False

async def test_insert_memory():
    """Test inserting a test memory."""
    try:
        test_data = {
            'content': 'Test memory content',
            'user_id': 'system',
            'metadata': {
                'url': 'https://test.com',
                'title': 'Test Memory',
                'tier': 0
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/climate_memories",
                headers=SUPABASE_HEADERS,
                json=test_data
            )
            
            if response.status_code == 201:
                logger.info("✅ Successfully inserted test memory")
                # Clean up test data
                memory_id = response.json()[0]['id']
                await client.delete(
                    f"{SUPABASE_URL}/rest/v1/climate_memories?id=eq.{memory_id}",
                    headers=SUPABASE_HEADERS
                )
                return True
            else:
                logger.error(f"❌ Failed to insert test memory: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Error testing memory insertion: {str(e)}")
        return False

async def main():
    """Run all tests."""
    logger.info("Starting Supabase configuration tests...")
    
    # Test connection
    if not await test_supabase_connection():
        return
    
    # Test vector extension
    if not await test_vector_extension():
        return
    
    # Test table structure
    if not await test_climate_memories_table():
        return
    
    # Test memory insertion
    if not await test_insert_memory():
        return
    
    logger.info("✅ All tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 