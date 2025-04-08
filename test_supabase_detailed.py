#!/usr/bin/env python3
"""
Detailed test script for Supabase connection with schema inspection and data operations.
"""

import os
import sys
import json
import httpx
import uuid
from datetime import datetime

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

print(f'URL: {url}, Key available: {"Yes" if key else "No"}')

if not url or not key:
    print("Error: Supabase credentials are missing. Please check environment variables.")
    sys.exit(1)

# Headers for Supabase API requests
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

# Test the connection
print("\n===== Detailed Supabase Test =====")

# 1. Check companies table schema
print("\n1. Inspecting 'companies' table schema:")
try:
    # Get information about the table (PostgreSQL information_schema)
    response = httpx.get(
        f"{url}/rest/v1/companies?limit=0",
        headers=headers
    )
    
    if response.status_code == 200:
        # Try to get the column names from response headers
        range_header = response.headers.get('content-range', '')
        
        # Use a direct query to get column information
        query = "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'companies'"
        schema_response = httpx.post(
            f"{url}/rest/v1/rpc/execute_sql",
            headers=headers,
            json={"query": query}
        )
        
        if schema_response.status_code == 200:
            columns = schema_response.json()
            print(f"✅ Table schema retrieved successfully!")
            print("\nColumn details:")
            for column in columns:
                print(f"  - {column['column_name']}: {column['data_type']} (Nullable: {column['is_nullable']})")
        else:
            print(f"⚠️ Could not retrieve detailed schema: {schema_response.status_code}")
            print(f"   Let's try to infer schema from sample data...")
            
            # Get sample data to infer schema
            sample_response = httpx.get(
                f"{url}/rest/v1/companies?limit=1",
                headers=headers
            )
            
            if sample_response.status_code == 200 and sample_response.json():
                sample = sample_response.json()[0]
                print("\nInferred schema from sample data:")
                for key, value in sample.items():
                    type_name = type(value).__name__ if value is not None else "null"
                    print(f"  - {key}: {type_name}")
    else:
        print(f"❌ Error accessing companies table: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
except Exception as e:
    print(f"❌ Error inspecting schema: {str(e)}")

# 2. Test data insertion (Profile)
print("\n2. Testing data insertion:")
try:
    # Check if profiles table exists
    response = httpx.get(
        f"{url}/rest/v1/profiles?limit=0",
        headers=headers
    )
    
    if response.status_code == 404:
        print("❌ Profiles table doesn't exist. Creating it...")
        # Create profiles table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS profiles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            location TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            is_veteran BOOLEAN DEFAULT FALSE,
            is_ej_community BOOLEAN DEFAULT FALSE,
            gateway_city TEXT,
            user_type TEXT
        );
        """
        
        create_response = httpx.post(
            f"{url}/rest/v1/rpc/execute_sql",
            headers=headers,
            json={"query": create_table_query}
        )
        
        if create_response.status_code in [200, 201]:
            print("✅ Profiles table created successfully!")
        else:
            print(f"❌ Failed to create profiles table: {create_response.status_code}")
            print(f"   Response: {create_response.text[:100]}...")
            print("\nTrying insertion anyway...")
    
    # Attempt to insert test profile data
    test_profile = {
        "user_id": str(uuid.uuid4()),
        "name": "Test User",
        "email": "test@example.com",
        "location": "Boston",
        "is_veteran": False,
        "is_ej_community": True,
        "gateway_city": "Boston",
        "user_type": "Career Transitioner",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    insert_response = httpx.post(
        f"{url}/rest/v1/profiles",
        headers=headers,
        json=test_profile
    )
    
    if insert_response.status_code in [200, 201, 204]:
        print(f"✅ Test profile inserted successfully!")
        # Retrieve the inserted profile
        get_response = httpx.get(
            f"{url}/rest/v1/profiles?user_id=eq.{test_profile['user_id']}",
            headers=headers
        )
        
        if get_response.status_code == 200 and get_response.json():
            print(f"✅ Retrieved the inserted profile!")
            print(f"   Profile ID: {get_response.json()[0].get('id')}")
        else:
            print(f"⚠️ Could not retrieve inserted profile: {get_response.status_code}")
    else:
        print(f"❌ Failed to insert test profile: {insert_response.status_code}")
        print(f"   Response: {insert_response.text[:200]}...")

except Exception as e:
    print(f"❌ Error during data insertion test: {str(e)}")

print("\n===== Test Completed =====") 