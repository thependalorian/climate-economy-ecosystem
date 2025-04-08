#!/usr/bin/env python3
"""
Test script for verifying the Supabase connection and database setup.
This script can be used to ensure that your Supabase configuration is correct
and that you can access the necessary tables.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to path so we can import the utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_supabase.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_supabase")

# Load environment variables
load_dotenv()

async def test_supabase_connection():
    """Test the connection to Supabase."""
    logger.info("Testing Supabase connection...")
    
    try:
        # Initialize the Supabase client
        client = SupabaseClient()
        
        # Test the connection
        connection_result = await client.test_connection()
        
        if connection_result["status"] == "success":
            logger.info("✅ Successfully connected to Supabase")
        else:
            logger.error(f"❌ Failed to connect to Supabase: {connection_result['message']}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing Supabase connection: {str(e)}")
        return False

async def test_memories_table():
    """Test access to the memories table."""
    logger.info("Testing access to the memories table...")
    
    try:
        # Initialize the Supabase client
        client = SupabaseClient()
        
        # Fetch memories (limit to 5 for testing)
        memories = await client.fetch_memories(limit=5)
        
        if memories:
            logger.info(f"✅ Successfully fetched {len(memories)} memories")
            logger.info(f"  Sample memory ID: {memories[0].get('id', 'N/A')}")
            logger.info(f"  Sample memory URL: {memories[0].get('source_url', 'N/A')}")
        else:
            logger.warning("⚠️ No memories found - table may be empty")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing memories table: {str(e)}")
        return False

async def test_organizations_table():
    """Test access to the organizations table."""
    logger.info("Testing access to the organizations table...")
    
    try:
        # Initialize the Supabase client
        client = SupabaseClient()
        
        # Fetch organizations
        organizations = await client.fetch_organizations()
        
        if organizations:
            logger.info(f"✅ Successfully fetched {len(organizations)} organizations")
            logger.info(f"  Sample organization: {organizations[0].get('name', 'N/A')}")
        else:
            logger.warning("⚠️ No organizations found - table may be empty")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing organizations table: {str(e)}")
        return False

async def test_organization_types_table():
    """Test access to the organization_types table."""
    logger.info("Testing access to the organization_types table...")
    
    try:
        # Initialize the Supabase client
        client = SupabaseClient()
        
        # Fetch organization types
        org_types = await client.fetch_organization_types()
        
        if org_types:
            logger.info(f"✅ Successfully fetched {len(org_types)} organization types")
            logger.info(f"  Sample organization type: {org_types[0].get('name', 'N/A')}")
        else:
            logger.warning("⚠️ No organization types found - table may be empty")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing organization_types table: {str(e)}")
        return False

async def test_search_memories():
    """Test the search_memories function."""
    logger.info("Testing memory search functionality...")
    
    try:
        # Initialize the Supabase client
        client = SupabaseClient()
        
        # Search for memories containing "climate"
        search_results = await client.search_memories("climate", limit=5)
        
        if search_results:
            logger.info(f"✅ Successfully searched memories, found {len(search_results)} results")
        else:
            logger.warning("⚠️ No search results found - try a different search term")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing memory search: {str(e)}")
        return False

async def run_all_tests():
    """Run all Supabase tests."""
    logger.info("Starting Supabase tests...")
    
    # Test connection
    connection_ok = await test_supabase_connection()
    if not connection_ok:
        logger.error("❌ Connection test failed - aborting further tests")
        return False
    
    # Test tables
    memories_ok = await test_memories_table()
    organizations_ok = await test_organizations_table()
    org_types_ok = await test_organization_types_table()
    search_ok = await test_search_memories()
    
    # Check results
    all_ok = connection_ok and memories_ok and organizations_ok and org_types_ok and search_ok
    
    if all_ok:
        logger.info("✅ All Supabase tests passed")
    else:
        logger.warning("⚠️ Some Supabase tests failed")
    
    return all_ok

def print_env_info():
    """Print information about the environment."""
    logger.info("Environment information:")
    
    # Check Supabase URL
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        logger.info(f"  SUPABASE_URL: {supabase_url[:10]}...{supabase_url[-5:]}")
    else:
        logger.error("  SUPABASE_URL: Not found in environment variables")
    
    # Check Supabase key (don't print the actual key)
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    if supabase_key:
        logger.info(f"  SUPABASE_SERVICE_KEY: {supabase_key[:5]}...{supabase_key[-5:]}")
    else:
        logger.error("  SUPABASE_SERVICE_KEY: Not found in environment variables")
    
    # Check OpenAI key (don't print the actual key)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        logger.info(f"  OPENAI_API_KEY: {openai_key[:5]}...{openai_key[-5:]}")
    else:
        logger.warning("  OPENAI_API_KEY: Not found in environment variables (not required for tests)")

async def main():
    """Main function."""
    print("\n" + "=" * 50)
    print(" CLIMATE ECONOMY ECOSYSTEM - SUPABASE TEST ")
    print("=" * 50 + "\n")
    
    # Print environment information
    print_env_info()
    
    # Run tests
    result = await run_all_tests()
    
    print("\n" + "=" * 50)
    if result:
        print(" ✅ SUPABASE TESTS COMPLETED SUCCESSFULLY ")
    else:
        print(" ❌ SUPABASE TESTS FAILED ")
    print("=" * 50 + "\n")
    
    print("Check test_supabase.log for detailed information.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 