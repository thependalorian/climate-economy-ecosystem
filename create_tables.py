#!/usr/bin/env python3
"""
Script to create missing tables in Supabase.
This script attempts to use various methods to create tables:
1. REST API with table creation
2. Direct SQL execution if available
3. Output SQL commands for manual execution
"""

import os
import sys
import httpx
import json
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
    'Prefer': 'return=representation'
}

# SQL definitions for tables
TABLE_DEFINITIONS = {
    'profiles': """
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
    -- Enable Row Level Security
    ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
    -- Create policies
    CREATE POLICY "Users can view their own profile"
        ON public.profiles
        FOR SELECT
        USING (auth.uid() = user_id);
    CREATE POLICY "Users can update their own profile"
        ON public.profiles
        FOR UPDATE
        USING (auth.uid() = user_id);
    CREATE POLICY "Users can insert their own profile"
        ON public.profiles
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
    """,

    'job_matches': """
    CREATE TABLE IF NOT EXISTS public.job_matches (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    -- Enable Row Level Security
    ALTER TABLE public.job_matches ENABLE ROW LEVEL SECURITY;
    -- Create policies
    CREATE POLICY "Users can view their own job matches"
        ON public.job_matches
        FOR SELECT
        USING (auth.uid() = user_id);
    CREATE POLICY "Users can insert their own job matches"
        ON public.job_matches
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
    CREATE POLICY "Users can update their own job matches"
        ON public.job_matches
        FOR UPDATE
        USING (auth.uid() = user_id);
    """,

    'chats': """
    CREATE TABLE IF NOT EXISTS public.chats (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID,
        message TEXT NOT NULL,
        role TEXT NOT NULL,
        context JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    -- Enable Row Level Security
    ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
    -- Create policies
    CREATE POLICY "Users can view their own chats"
        ON public.chats
        FOR SELECT
        USING (auth.uid() = user_id);
    CREATE POLICY "Users can insert their own chats"
        ON public.chats
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
    """,

    'activity_log': """
    CREATE TABLE IF NOT EXISTS public.activity_log (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID,
        action TEXT NOT NULL,
        details JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    -- Enable Row Level Security
    ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;
    -- Create policies
    CREATE POLICY "Users can view their own activity logs"
        ON public.activity_log
        FOR SELECT
        USING (auth.uid() = user_id);
    CREATE POLICY "Users can insert activity logs"
        ON public.activity_log
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
    """
}

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

# Attempt to run SQL directly through Supabase
def try_direct_sql_execution(sql):
    """Try to execute SQL directly using various Supabase endpoints."""
    # Method 1: Try using the sql endpoint
    try:
        response = httpx.post(
            f"{url}/rest/v1/sql",
            headers=headers,
            json={"query": sql}
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info("✅ SQL executed successfully using /sql endpoint")
            return True
        else:
            logger.info(f"⚠️ SQL execution using /sql endpoint failed: {response.status_code}")
    except Exception as e:
        logger.info(f"⚠️ Error using /sql endpoint: {str(e)}")

    # Method 2: Try using rpc with an execute_sql function
    try:
        response = httpx.post(
            f"{url}/rest/v1/rpc/execute_sql",
            headers=headers,
            json={"query": sql}
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info("✅ SQL executed successfully using RPC execute_sql")
            return True
        else:
            logger.info(f"⚠️ SQL execution using RPC failed: {response.status_code}")
    except Exception as e:
        logger.info(f"⚠️ Error using RPC: {str(e)}")

    # Method 3: Try using the functions endpoint
    try:
        response = httpx.post(
            f"{url}/rest/v1/postgres/execute",
            headers=headers,
            json={"sql": sql}
        )
        
        if response.status_code in [200, 201, 204]:
            logger.info("✅ SQL executed successfully using postgres execute")
            return True
        else:
            logger.info(f"⚠️ SQL execution using postgres execute failed: {response.status_code}")
    except Exception as e:
        logger.info(f"⚠️ Error using postgres execute: {str(e)}")
    
    return False

# Create table in Supabase
def create_table(table_name):
    """Create a table in Supabase."""
    logger.info(f"Trying to create table: {table_name}")
    
    if table_exists(table_name):
        logger.info(f"✅ Table {table_name} already exists")
        return True
    
    # Get SQL definition
    sql = TABLE_DEFINITIONS.get(table_name)
    if not sql:
        logger.error(f"❌ No SQL definition found for table {table_name}")
        return False
    
    # Try direct SQL execution
    if try_direct_sql_execution(sql):
        logger.info(f"✅ Table {table_name} created successfully using SQL")
        return True
    
    # If we get here, direct SQL execution failed
    logger.warning(f"⚠️ Could not create table {table_name} using API methods")
    logger.info(f"⚠️ Please create the table manually using the SQL below:\n{sql}")
    return False

# Main function
def main():
    """Create missing tables in Supabase."""
    logger.info("Starting table creation...")
    
    tables_to_create = [
        'profiles',
        'job_matches',
        'chats',
        'activity_log'
    ]
    
    success_count = 0
    manual_sql_needed = []
    
    for table in tables_to_create:
        if create_table(table):
            success_count += 1
        else:
            manual_sql_needed.append(table)
    
    # Summary
    logger.info("\n===== Creation Summary =====")
    logger.info(f"Total tables attempted: {len(tables_to_create)}")
    logger.info(f"Tables successfully created: {success_count}")
    
    if manual_sql_needed:
        logger.info("\n⚠️ The following tables need to be created manually:")
        for table in manual_sql_needed:
            logger.info(f"  - {table}")
        
        logger.info("\nTo create these tables manually:")
        logger.info("1. Log into your Supabase dashboard")
        logger.info("2. Navigate to the SQL Editor")
        logger.info("3. Copy and paste the SQL for each table below")
        logger.info("4. Run the SQL and check if the tables are created")
        
        for table in manual_sql_needed:
            logger.info(f"\n--- SQL for {table} ---\n{TABLE_DEFINITIONS[table]}")
    else:
        logger.info("\n✅ All tables created successfully!")
    
    # Check if all tables exist now
    logger.info("\nVerifying table existence:")
    for table in tables_to_create:
        exists = table_exists(table)
        status = "✅" if exists else "❌"
        logger.info(f"  - {table}: {status}")

if __name__ == "__main__":
    main() 