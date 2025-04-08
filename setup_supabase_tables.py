#!/usr/bin/env python3
"""
Script to set up missing Supabase tables through the REST API.
This script will create the following tables if they don't exist:
1. profiles
2. job_matches
3. chats
4. activity_log
"""

import os
import sys
import httpx
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv
import json

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
    'Content-Type': 'application/json'
}

# Create RPC function to execute SQL
def execute_sql(sql_statement):
    """Execute SQL statement using Supabase REST API."""
    try:
        # First, check if the execute_sql RPC function exists
        rpc_endpoint = f"{url}/rest/v1/rpc/execute_sql"
        test_response = httpx.post(
            rpc_endpoint,
            headers=headers,
            json={"query": "SELECT 1"}
        )
        
        # If the RPC function doesn't exist, we'll create it
        if test_response.status_code == 404:
            logger.info("Creating execute_sql RPC function...")
            
            # Create the function using the REST API
            sql_function = """
            CREATE OR REPLACE FUNCTION execute_sql(query text)
            RETURNS json
            LANGUAGE plpgsql
            SECURITY DEFINER
            AS $$
            DECLARE
                result json;
            BEGIN
                EXECUTE query;
                result := json_build_object('success', true, 'message', 'SQL executed successfully');
                RETURN result;
            EXCEPTION WHEN OTHERS THEN
                result := json_build_object('success', false, 'message', SQLERRM);
                RETURN result;
            END;
            $$;
            """
            
            # We need to use the SQL API directly
            sql_endpoint = f"{url}/rest/v1/sql"
            create_function_response = httpx.post(
                sql_endpoint,
                headers=headers,
                json={"query": sql_function}
            )
            
            if create_function_response.status_code not in [200, 201]:
                logger.error(f"Failed to create RPC function: {create_function_response.status_code}")
                logger.error(f"Response: {create_function_response.text}")
                return False
            
            logger.info("✅ execute_sql RPC function created")
        
        # Execute the SQL statement
        response = httpx.post(
            rpc_endpoint,
            headers=headers,
            json={"query": sql_statement}
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info("✅ SQL executed successfully")
            return True
        else:
            logger.error(f"❌ Failed to execute SQL: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error executing SQL: {str(e)}")
        return False

# Check if table exists
def table_exists(table_name):
    """Check if table exists in Supabase."""
    try:
        response = httpx.get(
            f"{url}/rest/v1/{table_name}?limit=0",
            headers=headers
        )
        
        return response.status_code == 200
    except Exception:
        return False

# Create profiles table
def create_profiles_table():
    """Create profiles table if it doesn't exist."""
    logger.info("Creating profiles table...")
    
    if table_exists('profiles'):
        logger.info("✅ profiles table already exists")
        return True
    
    sql = """
    CREATE TABLE IF NOT EXISTS public.profiles (
        id UUID PRIMARY KEY,
        user_id UUID NOT NULL,
        email TEXT,
        name TEXT,
        location TEXT,
        user_type TEXT,
        is_veteran BOOLEAN DEFAULT FALSE,
        is_ej_community BOOLEAN DEFAULT FALSE,
        gateway_city TEXT,
        resume_url TEXT,
        skills TEXT[],
        experience_level TEXT,
        preferred_sectors TEXT[],
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    return execute_sql(sql)

# Create job_matches table
def create_job_matches_table():
    """Create job_matches table if it doesn't exist."""
    logger.info("Creating job_matches table...")
    
    if table_exists('job_matches'):
        logger.info("✅ job_matches table already exists")
        return True
    
    sql = """
    CREATE TABLE IF NOT EXISTS public.job_matches (
        id UUID PRIMARY KEY,
        user_id UUID NOT NULL,
        job_id UUID,
        company_name TEXT,
        job_title TEXT,
        match_score INTEGER,
        status TEXT,
        location TEXT,
        url TEXT,
        applied_date TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    return execute_sql(sql)

# Create chats table
def create_chats_table():
    """Create chats table if it doesn't exist."""
    logger.info("Creating chats table...")
    
    if table_exists('chats'):
        logger.info("✅ chats table already exists")
        return True
    
    sql = """
    CREATE TABLE IF NOT EXISTS public.chats (
        id UUID PRIMARY KEY,
        user_id UUID,
        message TEXT NOT NULL,
        role TEXT NOT NULL,
        context JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    return execute_sql(sql)

# Create activity_log table
def create_activity_log_table():
    """Create activity_log table if it doesn't exist."""
    logger.info("Creating activity_log table...")
    
    if table_exists('activity_log'):
        logger.info("✅ activity_log table already exists")
        return True
    
    sql = """
    CREATE TABLE IF NOT EXISTS public.activity_log (
        id UUID PRIMARY KEY,
        user_id UUID,
        action TEXT NOT NULL,
        details JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    return execute_sql(sql)

# Main function
def main():
    """Set up missing Supabase tables."""
    logger.info("Starting Supabase table setup...")
    
    # Attempt to create each table
    profiles = create_profiles_table()
    job_matches = create_job_matches_table()
    chats = create_chats_table()
    activity_log = create_activity_log_table()
    
    # Create a test entry in each table
    if profiles:
        try:
            logger.info("Creating test profile...")
            test_profile = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "email": f"test_{uuid.uuid4()}@example.com",
                "name": "Test User",
                "location": "Boston, MA",
                "user_type": "Job Seeker",
                "is_veteran": False,
                "is_ej_community": True,
                "gateway_city": "Boston",
                "skills": ["Solar Energy", "Project Management"],
                "experience_level": "Entry-Level",
                "preferred_sectors": ["Clean Energy", "Energy Efficiency"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = httpx.post(
                f"{url}/rest/v1/profiles",
                headers=headers,
                json=test_profile
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Test profile created successfully")
            else:
                logger.error(f"❌ Failed to create test profile: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error creating test profile: {str(e)}")
    
    # Summary
    logger.info("\n===== Setup Summary =====")
    logger.info(f"Profiles table: {'✅' if profiles else '❌'}")
    logger.info(f"Job matches table: {'✅' if job_matches else '❌'}")
    logger.info(f"Chats table: {'✅' if chats else '❌'}")
    logger.info(f"Activity log table: {'✅' if activity_log else '❌'}")
    
    if profiles and job_matches and chats and activity_log:
        logger.info("\n✅ All tables created successfully!")
    else:
        logger.warning("\n⚠️ Some tables could not be created.")
        logger.info("You may need to create these tables manually through the Supabase dashboard.")

if __name__ == "__main__":
    main() 