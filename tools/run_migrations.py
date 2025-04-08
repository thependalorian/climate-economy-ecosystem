#!/usr/bin/env python3

import os
import logging
import requests
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def run_sql_file(file_path: str) -> bool:
    """Run a SQL file against Supabase"""
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
            headers=headers,
            json={'sql': sql}
        )
        
        if response.status_code == 200:
            logging.info(f"Successfully ran migration: {file_path}")
            return True
        else:
            logging.error(f"Failed to run migration {file_path}: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Error running migration {file_path}: {str(e)}")
        return False

def main():
    """Main function to run migrations"""
    migrations_dir = Path(__file__).parent.parent / 'database' / 'migrations'
    
    # Get all SQL files in order
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    logging.info(f"Found {len(migration_files)} migration files")
    
    for migration_file in migration_files:
        logging.info(f"Running migration: {migration_file.name}")
        if not run_sql_file(str(migration_file)):
            logging.error(f"Failed to run migration {migration_file.name}")
            return
    
    logging.info("All migrations completed successfully")

if __name__ == "__main__":
    main() 