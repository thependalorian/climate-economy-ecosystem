#!/usr/bin/env python3
"""
Comprehensive test script for Supabase connectivity and operations.
This script will test:
1. Basic connectivity
2. Table existence and structure
3. CRUD operations
4. Vector extension (if applicable)
5. RPC functions
"""

import os
import sys
import json
import httpx
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

logger.info(f'URL: {url}, Key available: {"Yes" if key else "No"}')

if not url or not key:
    logger.error("Error: Supabase credentials are missing. Please check environment variables.")
    sys.exit(1)

# Headers for Supabase API requests
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'  # Return the inserted data
}

# Test tables to check
TABLES_TO_CHECK = [
    'companies',
    'profiles',
    'job_matches',
    'climate_memories',
    'training_programs',
    'chats',
    'activity_log'
]

def test_connection():
    """Test basic connection to Supabase."""
    logger.info("\n===== Testing Supabase Connection =====")
    try:
        # Make a request to the root URL
        response = httpx.get(
            f"{url}/rest/v1/",
            headers=headers
        )
        
        if response.status_code == 200:
            logger.info("✅ Successfully connected to Supabase!")
            available_endpoints = list(response.json().keys())
            logger.info(f"Available endpoints: {', '.join(available_endpoints)}")
            return True
        else:
            logger.error(f"❌ Failed to connect to Supabase: {response.status_code}")
            logger.error(f"Response: {response.text[:100]}...")
            return False
    except Exception as e:
        logger.error(f"❌ Error connecting to Supabase: {str(e)}")
        return False

def test_table_existence():
    """Test if required tables exist."""
    logger.info("\n===== Testing Table Existence =====")
    tables_status = {}
    
    for table in TABLES_TO_CHECK:
        try:
            # Test if table exists by querying with limit 0
            response = httpx.get(
                f"{url}/rest/v1/{table}?limit=0",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Table '{table}' exists")
                tables_status[table] = True
            elif response.status_code == 404:
                logger.warning(f"⚠️ Table '{table}' does not exist")
                tables_status[table] = False
            else:
                logger.error(f"❌ Error checking table '{table}': {response.status_code}")
                logger.error(f"Response: {response.text[:100]}...")
                tables_status[table] = False
        except Exception as e:
            logger.error(f"❌ Error checking table '{table}': {str(e)}")
            tables_status[table] = False
    
    return tables_status

def test_vector_extension():
    """Test if vector extension is working."""
    logger.info("\n===== Testing Vector Extension =====")
    try:
        # Test vector extension by calling test_vector RPC function
        test_vector = [0.1] * 1536  # Simple test vector
        
        response = httpx.post(
            f"{url}/rest/v1/rpc/test_vector",
            headers=headers,
            json={"v": test_vector}
        )
        
        if response.status_code in [200, 201]:
            logger.info("✅ Vector extension is working")
            return True
        else:
            logger.warning(f"⚠️ Vector extension test failed: {response.status_code}")
            logger.warning(f"This may be normal if you haven't set up vector search yet")
            logger.warning(f"Response: {response.text[:100]}...")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Vector extension test failed: {str(e)}")
        logger.warning("This may be normal if you haven't set up vector search yet")
        return False

def test_rpc_functions():
    """Test available RPC functions."""
    logger.info("\n===== Testing RPC Functions =====")
    try:
        # Check available RPC functions
        response = httpx.get(
            f"{url}/rest/v1/rpc",
            headers=headers
        )
        
        if response.status_code == 200:
            rpc_functions = response.json()
            if rpc_functions:
                logger.info(f"✅ Found {len(rpc_functions)} RPC functions")
                for func in rpc_functions:
                    logger.info(f"  - {func}")
            else:
                logger.info("ℹ️ No RPC functions found")
            return True
        else:
            logger.warning(f"⚠️ Could not retrieve RPC functions: {response.status_code}")
            logger.warning(f"Response: {response.text[:100]}...")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Error retrieving RPC functions: {str(e)}")
        return False

def test_crud_operations(tables_status):
    """Test CRUD operations on available tables."""
    logger.info("\n===== Testing CRUD Operations =====")
    
    # 1. Test companies table if it exists
    if tables_status.get('companies', False):
        logger.info("\n----- Testing Companies Table -----")
        try:
            # Create test company
            test_company = {
                "name": f"Test Company {uuid.uuid4()}",
                "location": "Test Location",
                "sector": "Test Sector",
                "description": "This is a test company created by the test script",
                "created_at": datetime.now().isoformat()
            }
            
            # 1. Insert
            insert_response = httpx.post(
                f"{url}/rest/v1/companies",
                headers=headers,
                json=test_company
            )
            
            if insert_response.status_code in [200, 201]:
                logger.info("✅ Successfully inserted test company")
                company_data = insert_response.json()[0]
                company_id = company_data.get('id')
                logger.info(f"Company ID: {company_id}")
                
                # 2. Retrieve
                get_response = httpx.get(
                    f"{url}/rest/v1/companies?id=eq.{company_id}",
                    headers=headers
                )
                
                if get_response.status_code == 200:
                    logger.info("✅ Successfully retrieved test company")
                    
                    # 3. Update
                    update_data = {"description": "Updated test description"}
                    update_response = httpx.patch(
                        f"{url}/rest/v1/companies?id=eq.{company_id}",
                        headers=headers,
                        json=update_data
                    )
                    
                    if update_response.status_code in [200, 204]:
                        logger.info("✅ Successfully updated test company")
                        
                        # 4. Delete
                        delete_response = httpx.delete(
                            f"{url}/rest/v1/companies?id=eq.{company_id}",
                            headers=headers
                        )
                        
                        if delete_response.status_code in [200, 204]:
                            logger.info("✅ Successfully deleted test company")
                        else:
                            logger.error(f"❌ Failed to delete test company: {delete_response.status_code}")
                    else:
                        logger.error(f"❌ Failed to update test company: {update_response.status_code}")
                else:
                    logger.error(f"❌ Failed to retrieve test company: {get_response.status_code}")
            else:
                logger.error(f"❌ Failed to insert test company: {insert_response.status_code}")
                logger.error(f"Response: {insert_response.text[:100]}...")
        except Exception as e:
            logger.error(f"❌ Error testing CRUD on companies table: {str(e)}")
    
    # 2. Test profiles table if it exists or try to create it
    logger.info("\n----- Testing Profiles Table -----")
    try:
        # Check if profiles table exists
        if not tables_status.get('profiles', False):
            logger.info("ℹ️ Profiles table doesn't exist, attempting to create a test profile anyway")
        
        # Create test profile
        test_profile = {
            "id": str(uuid.uuid4()),  # Using string UUID for id
            "user_id": str(uuid.uuid4()),
            "email": f"test_{uuid.uuid4()}@example.com",
            "name": "Test User",
            "location": "Test Location",
            "user_type": "Job Seeker",
            "is_veteran": False,
            "is_ej_community": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert test profile
        insert_response = httpx.post(
            f"{url}/rest/v1/profiles",
            headers=headers,
            json=test_profile
        )
        
        if insert_response.status_code in [200, 201]:
            logger.info("✅ Successfully inserted test profile")
            profile_data = insert_response.json()[0]
            profile_id = profile_data.get('id')
            logger.info(f"Profile ID: {profile_id}")
            
            # Retrieve
            get_response = httpx.get(
                f"{url}/rest/v1/profiles?id=eq.{profile_id}",
                headers=headers
            )
            
            if get_response.status_code == 200:
                logger.info("✅ Successfully retrieved test profile")
                
                # Delete
                delete_response = httpx.delete(
                    f"{url}/rest/v1/profiles?id=eq.{profile_id}",
                    headers=headers
                )
                
                if delete_response.status_code in [200, 204]:
                    logger.info("✅ Successfully deleted test profile")
                else:
                    logger.error(f"❌ Failed to delete test profile: {delete_response.status_code}")
            else:
                logger.error(f"❌ Failed to retrieve test profile: {get_response.status_code}")
        else:
            logger.error(f"❌ Failed to insert test profile: {insert_response.status_code}")
            logger.error(f"Response: {insert_response.text[:100]}...")
    except Exception as e:
        logger.error(f"❌ Error testing profiles table: {str(e)}")

def test_create_missing_tables(tables_status):
    """Test creating missing tables."""
    logger.info("\n===== Testing Table Creation =====")
    
    # Check which tables are missing
    missing_tables = [table for table, exists in tables_status.items() if not exists]
    if not missing_tables:
        logger.info("✅ All required tables exist!")
        return
    
    logger.info(f"ℹ️ Missing tables: {', '.join(missing_tables)}")
    
    # Try to create missing tables with sample data
    for table in missing_tables:
        logger.info(f"Attempting to create table: {table}")
        
        # Define sample data based on table name
        sample_data = None
        if table == 'profiles':
            sample_data = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "email": f"test_{uuid.uuid4()}@example.com",
                "name": "Test User",
                "location": "Boston, MA",
                "user_type": "Job Seeker",
                "is_veteran": False,
                "is_ej_community": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        elif table == 'job_matches':
            sample_data = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "job_id": str(uuid.uuid4()),
                "company_name": "Test Company",
                "job_title": "Test Position",
                "match_score": 85,
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        elif table == 'climate_memories':
            sample_data = {
                "id": str(uuid.uuid4()),
                "content": "Test climate memory content",
                "user_id": "system",
                "metadata": {
                    "title": "Test Memory",
                    "source": "Test Script",
                    "tier": 0
                },
                "created_at": datetime.now().isoformat()
            }
        elif table == 'training_programs':
            sample_data = {
                "id": str(uuid.uuid4()),
                "title": "Test Training Program",
                "provider": "Test Provider",
                "description": "This is a test training program",
                "location": "Boston, MA",
                "duration": "8 weeks",
                "created_at": datetime.now().isoformat()
            }
        elif table == 'chats':
            sample_data = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "message": "Test chat message",
                "role": "user",
                "created_at": datetime.now().isoformat()
            }
        elif table == 'activity_log':
            sample_data = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "action": "test_action",
                "details": {"source": "test script"},
                "created_at": datetime.now().isoformat()
            }
        
        if sample_data:
            try:
                # Attempt to insert sample data to create table
                insert_response = httpx.post(
                    f"{url}/rest/v1/{table}",
                    headers=headers,
                    json=sample_data
                )
                
                if insert_response.status_code in [200, 201]:
                    logger.info(f"✅ Successfully created table '{table}' with sample data")
                    
                    # Clean up the sample data
                    record_id = insert_response.json()[0].get('id')
                    delete_response = httpx.delete(
                        f"{url}/rest/v1/{table}?id=eq.{record_id}",
                        headers=headers
                    )
                    
                    if delete_response.status_code in [200, 204]:
                        logger.info(f"✅ Successfully cleaned up sample data from '{table}'")
                    else:
                        logger.warning(f"⚠️ Could not clean up sample data from '{table}': {delete_response.status_code}")
                else:
                    logger.error(f"❌ Failed to create table '{table}': {insert_response.status_code}")
                    logger.error(f"Response: {insert_response.text[:100]}...")
            except Exception as e:
                logger.error(f"❌ Error creating table '{table}': {str(e)}")
        else:
            logger.warning(f"⚠️ No sample data defined for table '{table}'")

def main():
    """Run all tests."""
    logger.info("Starting comprehensive Supabase tests...")
    
    # Test connection
    if not test_connection():
        logger.error("❌ Connection test failed. Exiting.")
        return
    
    # Test table existence
    tables_status = test_table_existence()
    
    # Test vector extension
    test_vector_extension()
    
    # Test RPC functions
    test_rpc_functions()
    
    # Test CRUD operations
    test_crud_operations(tables_status)
    
    # Test creating missing tables
    test_create_missing_tables(tables_status)
    
    logger.info("\n===== Test Summary =====")
    logger.info("Connection: ✅")
    logger.info("Table Status:")
    for table, exists in tables_status.items():
        status = "✅" if exists else "❌"
        logger.info(f"  - {table}: {status}")
    
    logger.info("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 