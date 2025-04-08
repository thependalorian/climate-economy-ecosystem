#!/usr/bin/env python3
"""
Open Supabase SQL Editor

This script opens the Supabase SQL Editor in your browser and provides
instructions for initializing the database.
"""

import sys
import logging
import webbrowser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def open_supabase_sql_editor():
    """Open the Supabase SQL Editor in the browser."""
    # Read the schema.sql file
    schema_path = Path(__file__).parent.parent / "supabase" / "schema.sql"
    
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return False
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    logger.info(f"Read schema file: {schema_path} ({len(schema_sql)} bytes)")
    
    # Open the Supabase dashboard
    url = "https://app.supabase.com/project/_/sql"
    logger.info(f"Opening Supabase SQL Editor: {url}")
    webbrowser.open(url)
    
    # Provide instructions
    logger.info("\nTo initialize the database, follow these steps:")
    logger.info("1. In the SQL Editor, click 'New query'")
    logger.info("2. Copy and paste the contents of schema.sql into the editor")
    logger.info("3. Click 'Run' to execute the SQL")
    
    # Print the path to the schema.sql file
    logger.info(f"\nSchema file path: {schema_path}")
    
    return True

def main():
    """Main function to open the Supabase SQL Editor."""
    logger.info("Opening Supabase SQL Editor...")
    
    success = open_supabase_sql_editor()
    
    if success:
        logger.info("Supabase SQL Editor opened successfully.")
    else:
        logger.error("Failed to open Supabase SQL Editor.")

if __name__ == "__main__":
    main()
