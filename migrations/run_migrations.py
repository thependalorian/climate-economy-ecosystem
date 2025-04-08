#!/usr/bin/env python3
"""
Database Migration Script for Climate Economy Ecosystem

This script runs SQL migrations to set up the necessary tables for the RLHF system.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migrations.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("migrations")

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

def run_migrations():
    """Run SQL migrations to set up the database schema"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return False
    
    try:
        # Initialize Supabase client
        logger.info("Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase successfully!")
        
        # Read migration SQL
        migration_file = os.path.join(os.path.dirname(__file__), "create_rlhf_tables.sql")
        with open(migration_file, "r") as f:
            migration_sql = f.read()
        
        # Split SQL into individual statements
        statements = migration_sql.split(";")
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    logger.info(f"Executing statement {i+1}/{len(statements)}...")
                    # Use RPC to execute raw SQL
                    response = supabase.rpc(
                        "exec_sql", 
                        {"sql_query": statement.strip() + ";"}
                    ).execute()
                    
                    if hasattr(response, 'error') and response.error:
                        logger.warning(f"Statement {i+1} warning: {response.error}")
                    else:
                        logger.info(f"Statement {i+1} executed successfully")
                except Exception as e:
                    logger.error(f"Error executing statement {i+1}: {str(e)}")
                    # Continue with other statements
        
        logger.info("Migrations completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    if not success:
        sys.exit(1)
