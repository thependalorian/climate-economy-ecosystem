#!/usr/bin/env python3
"""
Script to list all tables in the Supabase database and available RPC functions.
"""

import os
import sys
import httpx

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
    'Prefer': 'count=exact'  # To get total count
}

print("\n===== Supabase Database Inspection =====")

# 1. List all available endpoints
print("\n1. Listing available API endpoints:")
try:
    # Make a request to the Root URL
    response = httpx.get(
        f"{url}/rest/v1/",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Success!")
        print("\nAvailable endpoints (tables):")
        for endpoint in response.json().keys():
            print(f"  - {endpoint}")
    else:
        print(f"❌ Could not list endpoints: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
except Exception as e:
    print(f"❌ Error listing endpoints: {str(e)}")

# 2. Check for available RPC functions
print("\n2. Checking for available RPC functions:")
try:
    # Try accessing the RPC endpoint
    response = httpx.get(
        f"{url}/rest/v1/rpc",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ RPC endpoint is available")
        print("\nAvailable RPC functions:")
        for function in response.json():
            print(f"  - {function}")
    else:
        print(f"❌ Could not access RPC endpoint: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
except Exception as e:
    print(f"❌ Error checking RPC functions: {str(e)}")

# 3. Get detailed information about companies table
print("\n3. Getting detailed information about companies table:")
try:
    # Get specific company information
    response = httpx.get(
        f"{url}/rest/v1/companies?limit=1",
        headers=headers
    )
    
    if response.status_code == 200 and response.json():
        company = response.json()[0]
        print("✅ Company information retrieved!")
        print("\nCompany details:")
        for key, value in company.items():
            print(f"  - {key}: {value}")
            
    else:
        print(f"❌ Could not retrieve company information: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error retrieving company information: {str(e)}")

print("\n===== Inspection Completed =====") 