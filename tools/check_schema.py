#!/usr/bin/env python3

import os
import sys
import logging
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import from the root constants.py
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize base headers for Supabase requests
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def check_table_schema(table_name):
    """Check the schema of a table in Supabase."""
    try:
        logger.info(f"Checking schema for table: {table_name}")
        
        # Query the information_schema.columns table to get column information
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/information_schema/columns?select=column_name,data_type,is_nullable&table_name=eq.{table_name}",
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code != 200:
            logger.error(f"Error retrieving schema: {response.status_code} {response.text}")
            return None
        
        columns = response.json()
        logger.info(f"Found {len(columns)} columns in {table_name}")
        
        # Print column information
        for column in columns:
            logger.info(f"Column: {column['column_name']}, Type: {column['data_type']}, Nullable: {column['is_nullable']}")
        
        return columns
    except Exception as e:
        logger.error(f"Error checking schema: {str(e)}")
        return None

def check_table_data(table_name, limit=5):
    """Check sample data from a table in Supabase."""
    try:
        logger.info(f"Checking sample data from table: {table_name}")
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit={limit}",
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code != 200:
            logger.error(f"Error retrieving data: {response.status_code} {response.text}")
            return None
        
        data = response.json()
        logger.info(f"Retrieved {len(data)} records from {table_name}")
        
        # Print sample data (limited output for clarity)
        for i, record in enumerate(data):
            # Convert to JSON string with indentation for readability
            record_json = json.dumps(record, indent=2)
            # Truncate if too long
            truncated = record_json if len(record_json) < 500 else record_json[:500] + "..."
            logger.info(f"Record {i+1}: {truncated}")
        
        return data
    except Exception as e:
        logger.error(f"Error checking data: {str(e)}")
        return None

def list_tables():
    """List all tables in the public schema."""
    try:
        logger.info("Listing all tables in public schema")
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/information_schema/tables?select=table_name&table_schema=eq.public",
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code != 200:
            logger.error(f"Error listing tables: {response.status_code} {response.text}")
            return None
        
        tables = [table['table_name'] for table in response.json()]
        logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        return tables
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}")
        return None

def check_climate_memories():
    """Check the structure of the climate_memories table."""
    try:
        logger.info("Checking climate_memories table structure")
        
        # Get sample data to infer structure
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/climate_memories?select=*&limit=1",
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code != 200:
            logger.error(f"Error retrieving sample: {response.status_code} {response.text}")
            return None
        
        data = response.json()
        if not data:
            logger.info("No records found in climate_memories table")
            return None
            
        # Infer columns from first record
        record = data[0]
        logger.info(f"Columns in climate_memories: {', '.join(record.keys())}")
        
        # Print data types for each field
        for key, value in record.items():
            value_type = type(value).__name__
            example = str(value)[:100] + "..." if isinstance(value, str) and len(str(value)) > 100 else str(value)
            logger.info(f"Field: {key}, Type: {value_type}, Example: {example}")
        
        return record
    except Exception as e:
        logger.error(f"Error checking climate_memories: {str(e)}")
        return None

def main():
    """Main function."""
    try:
        # Test connection
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/climate_memories?select=id",
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code == 200:
            count = len(response.json())
            logger.info(f"Successfully connected to Supabase. Found {count} records.")
        else:
            logger.error(f"Failed to connect to Supabase: {response.status_code} {response.text}")
            return
        
        # Check climate_memories table structure
        check_climate_memories()
        
        # Check sample data
        check_table_data('climate_memories', 3)
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main() 