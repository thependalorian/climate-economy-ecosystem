#!/usr/bin/env python3
"""
Open Supabase SQL Editor with Strategy Tables Removal Script

This script opens the Supabase SQL Editor and provides instructions for
removing strategy-related tables to reduce database size.
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
    # Read the SQL script
    script_path = Path(__file__).parent.parent / "supabase" / "remove_strategy_tables.sql"
    
    if not script_path.exists():
        logger.error(f"SQL script not found: {script_path}")
        return False
    
    with open(script_path, 'r') as f:
        sql_script = f.read()
    
    logger.info(f"Read SQL script: {script_path} ({len(sql_script)} bytes)")
    
    # Open the Supabase dashboard
    url = "https://app.supabase.com/project/_/sql"
    logger.info(f"Opening Supabase SQL Editor: {url}")
    webbrowser.open(url)
    
    # Provide instructions
    logger.info("\nTo remove strategy-related tables, follow these steps:")
    logger.info("1. In the SQL Editor, click 'New query'")
    logger.info("2. Copy and paste the contents of remove_strategy_tables.sql into the editor")
    logger.info("3. Click 'Run' to execute the SQL")
    logger.info("\nWARNING: This will permanently delete all strategy-related tables and their data.")
    logger.info("If you want to back up the data first, uncomment the backup line in the script.")
    
    # Print the path to the SQL script
    logger.info(f"\nSQL script path: {script_path}")
    
    # Print the SQL script
    logger.info("\nSQL script content:")
    logger.info("----------------------------------------")
    logger.info(sql_script)
    logger.info("----------------------------------------")
    
    return True

def main():
    """Main function to open the Supabase SQL Editor."""
    logger.info("Opening Supabase SQL Editor with strategy tables removal script...")
    
    success = open_supabase_sql_editor()
    
    if success:
        logger.info("Supabase SQL Editor opened successfully.")
    else:
        logger.error("Failed to open Supabase SQL Editor.")

if __name__ == "__main__":
    main()
