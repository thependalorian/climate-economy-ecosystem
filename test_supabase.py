#!/usr/bin/env python3
"""
Test script for Supabase connection using direct HTTP requests.
"""

import os
import sys
import json
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
    'Content-Type': 'application/json'
}

# Test the connection
print("\nTesting connection to Supabase...")

# Define tables to test
tables = ['companies', 'profiles', 'job_matches', 'activity_log']

for i, table in enumerate(tables, 1):
    print(f"\n{i}. Testing '{table}' table:")
    try:
        # Make a direct HTTP request
        response = httpx.get(
            f"{url}/rest/v1/{table}?select=*&limit=5",
            headers=headers
        )
        
        # Check response status
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} records")
            
            if data and len(data) > 0:
                first_item = data[0]
                key_to_show = next(iter(first_item.keys()), 'id')
                print(f"   First record {key_to_show}: {first_item.get(key_to_show, 'Unknown')}")
            
        elif response.status_code == 404:
            print(f"❌ Table '{table}' not found. Status code: 404")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\nTest completed.") 