#!/usr/bin/env python3
"""
Direct table creation in Supabase using httpx for direct API access.
"""

import os
import sys
import json
import logging
import uuid
import httpx
from datetime import datetime
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

# Configure Supabase headers
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Function to check if a table exists
def table_exists(table_name):
    """Check if a table exists in Supabase."""
    try:
        # Try to select 0 rows from the table
        response = httpx.get(
            f"{url}/rest/v1/{table_name}?limit=0",
            headers=headers
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Table {table_name} does not exist or is not accessible: {str(e)}")
        return False

# Function to create a sample profile
def create_sample_profile():
    """Create a sample profile in the profiles table."""
    try:
        profile_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        profile_data = {
            "id": profile_id,
            "user_id": user_id,
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
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
            json=profile_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info(f"✅ Sample profile created with ID: {profile_id}")
            return True
        else:
            logger.error(f"Failed to create sample profile: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample profile: {str(e)}")
        return False

# Function to create a sample job match
def create_sample_job_match():
    """Create a sample job match in the job_matches table."""
    try:
        job_match_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        job_match_data = {
            "id": job_match_id,
            "user_id": user_id,
            "company_name": "EcoTech Solutions",
            "job_title": "Solar Panel Installer",
            "match_score": 85,
            "status": "open",
            "location": "Boston, MA",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        response = httpx.post(
            f"{url}/rest/v1/job_matches",
            headers=headers,
            json=job_match_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info(f"✅ Sample job match created with ID: {job_match_id}")
            return True
        else:
            logger.error(f"Failed to create sample job match: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample job match: {str(e)}")
        return False

# Function to create a sample chat message
def create_sample_chat():
    """Create a sample chat message in the chats table."""
    try:
        chat_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        chat_data = {
            "id": chat_id,
            "user_id": user_id,
            "message": "Hello, I am looking for solar energy jobs in Boston.",
            "role": "user",
            "context": {
                "location": "Boston",
                "sector": "Solar Energy"
            },
            "created_at": datetime.now().isoformat()
        }
        
        response = httpx.post(
            f"{url}/rest/v1/chats",
            headers=headers,
            json=chat_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info(f"✅ Sample chat created with ID: {chat_id}")
            return True
        else:
            logger.error(f"Failed to create sample chat: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample chat: {str(e)}")
        return False

# Function to create a sample activity log
def create_sample_activity_log():
    """Create a sample activity log in the activity_log table."""
    try:
        log_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        log_data = {
            "id": log_id,
            "user_id": user_id,
            "action": "profile_updated",
            "details": {
                "fields": ["skills", "location"]
            },
            "created_at": datetime.now().isoformat()
        }
        
        response = httpx.post(
            f"{url}/rest/v1/activity_log",
            headers=headers,
            json=log_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info(f"✅ Sample activity log created with ID: {log_id}")
            return True
        else:
            logger.error(f"Failed to create sample activity log: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating sample activity log: {str(e)}")
        return False

# Main function
def main():
    """Create sample data in Supabase tables."""
    logger.info("Starting direct Supabase table testing...")
    
    # Check if tables exist
    tables = [
        "profiles",
        "job_matches",
        "chats",
        "activity_log"
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in tables:
        if table_exists(table):
            logger.info(f"✅ Table '{table}' exists")
            existing_tables.append(table)
        else:
            logger.warning(f"❌ Table '{table}' does not exist")
            missing_tables.append(table)
    
    # If all tables exist, try creating sample data
    if not missing_tables:
        logger.info("All required tables exist. Creating sample data...")
        
        # Create sample data
        profile_created = create_sample_profile()
        job_match_created = create_sample_job_match()
        chat_created = create_sample_chat()
        activity_log_created = create_sample_activity_log()
        
        # Summarize results
        logger.info("\n===== Sample Data Creation Summary =====")
        logger.info(f"Sample profile: {'✅' if profile_created else '❌'}")
        logger.info(f"Sample job match: {'✅' if job_match_created else '❌'}")
        logger.info(f"Sample chat: {'✅' if chat_created else '❌'}")
        logger.info(f"Sample activity log: {'✅' if activity_log_created else '❌'}")
        
        if profile_created and job_match_created and chat_created and activity_log_created:
            logger.info("\n✅ All sample data created successfully!")
        else:
            logger.warning("\n⚠️ Some sample data could not be created.")
    else:
        logger.error("\n❌ Cannot create sample data because some tables are missing")
        logger.info("Please run the SQL script in the Supabase SQL Editor to create the missing tables.")
        
        # Print SQL for creating missing tables
        logger.info("\nSQL to create missing tables:")
        
        if "profiles" in missing_tables:
            logger.info("""
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            """)
            
        if "job_matches" in missing_tables:
            logger.info("""
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
            """)
            
        if "chats" in missing_tables:
            logger.info("""
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    message TEXT NOT NULL,
    role TEXT NOT NULL,
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
            """)
            
        if "activity_log" in missing_tables:
            logger.info("""
CREATE TABLE IF NOT EXISTS public.activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
            """)

if __name__ == "__main__":
    main() 