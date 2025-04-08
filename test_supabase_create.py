#!/usr/bin/env python3
"""
Script to test creating tables and inserting data in Supabase using the REST API.
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
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'  # Return the inserted data
}

print("\n===== Supabase Data Creation Test =====")

# 1. Insert a new company
print("\n1. Inserting a new company:")
try:
    # Create new company data
    new_company = {
        "name": "EcoTech Solutions",
        "location": "Boston, MA",
        "sector": "Energy Efficiency",
        "description": "Specializing in smart building technology and energy audits",
        "created_at": datetime.now().isoformat()
    }
    
    # Insert the company
    response = httpx.post(
        f"{url}/rest/v1/companies",
        headers=headers,
        json=new_company
    )
    
    if response.status_code in [200, 201, 204]:
        print("✅ New company inserted successfully!")
        if response.json():
            company_id = response.json()[0].get('id')
            print(f"   Company ID: {company_id}")
    else:
        print(f"❌ Failed to insert new company: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
except Exception as e:
    print(f"❌ Error inserting new company: {str(e)}")

# 2. Try creating a profiles table if it doesn't exist
print("\n2. Creating a profiles table (if needed):")

# First check if the profiles table exists already
try:
    check_response = httpx.get(
        f"{url}/rest/v1/profiles?limit=0",
        headers=headers
    )
    
    if check_response.status_code == 404:
        print("👉 Profiles table doesn't exist, we'll create it.")
        
        # Prepare a SQL statement for creating the table
        # Note: We'll need to make a server-side function for this
        print("⚠️ Direct SQL execution not available. We need to use other means.")
        print("👉 Let's try to create the table by sending a POST request with the right structure.")
        
        # Try creating a test profile anyway - Supabase might auto-create the table
        test_profile = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Jane Doe",
            "email": "jane@example.com",
            "location": "Cambridge, MA",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_veteran": True,
            "is_ej_community": False,
            "gateway_city": None,
            "user_type": "Veteran"
        }
        
        profile_response = httpx.post(
            f"{url}/rest/v1/profiles",
            headers=headers,
            json=test_profile
        )
        
        if profile_response.status_code in [200, 201, 204]:
            print("✅ Test profile created! Table was either created or already existed.")
            if profile_response.json():
                profile_id = profile_response.json()[0].get('id')
                print(f"   Profile ID: {profile_id}")
        else:
            print(f"❌ Failed to create profile: {profile_response.status_code}")
            print(f"   Response: {profile_response.text[:100]}...")
    else:
        print("✅ Profiles table already exists!")
        
        # Retrieve all profiles
        get_profiles = httpx.get(
            f"{url}/rest/v1/profiles",
            headers=headers
        )
        
        if get_profiles.status_code == 200:
            profiles = get_profiles.json()
            print(f"   Found {len(profiles)} existing profiles")
            
            # Insert a new profile
            new_profile = {
                "user_id": str(uuid.uuid4()),
                "name": "John Smith",
                "email": "john@example.com",
                "location": "Worcester, MA",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_veteran": False,
                "is_ej_community": True,
                "gateway_city": "Worcester",
                "user_type": "EJ Community Member"
            }
            
            insert_response = httpx.post(
                f"{url}/rest/v1/profiles",
                headers=headers,
                json=new_profile
            )
            
            if insert_response.status_code in [200, 201, 204]:
                print("✅ New profile inserted successfully!")
                if insert_response.json():
                    new_profile_id = insert_response.json()[0].get('id')
                    print(f"   New Profile ID: {new_profile_id}")
            else:
                print(f"❌ Failed to insert new profile: {insert_response.status_code}")
                print(f"   Response: {insert_response.text[:100]}...")
        else:
            print(f"❌ Could not retrieve profiles: {get_profiles.status_code}")
            
except Exception as e:
    print(f"❌ Error working with profiles table: {str(e)}")

# 3. Create job_matches table (if it doesn't exist)
print("\n3. Testing job_matches table:")
try:
    check_response = httpx.get(
        f"{url}/rest/v1/job_matches?limit=0",
        headers=headers
    )
    
    if check_response.status_code == 404:
        print("👉 job_matches table doesn't exist yet")
        # Try to insert a job match anyway - Supabase might auto-create the table
        job_match = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "job_id": str(uuid.uuid4()),
            "company_name": "EcoTech Solutions",
            "job_title": "Energy Efficiency Consultant",
            "match_score": 85,
            "status": "applied",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        match_response = httpx.post(
            f"{url}/rest/v1/job_matches",
            headers=headers,
            json=job_match
        )
        
        if match_response.status_code in [200, 201, 204]:
            print("✅ Test job match created! Table was either created or already existed.")
        else:
            print(f"❌ Failed to create job match: {match_response.status_code}")
            print(f"   Response: {match_response.text[:100]}...")
    else:
        print("✅ job_matches table already exists!")
        
except Exception as e:
    print(f"❌ Error testing job_matches table: {str(e)}")

print("\n===== Test Completed =====") 