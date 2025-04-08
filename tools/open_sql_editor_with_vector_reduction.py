#!/usr/bin/env python3
"""
Open Supabase SQL Editor with Vector Embeddings Reduction Script

This script opens the Supabase SQL Editor and provides instructions for
reducing the size of vector embeddings in the database.
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
    script_path = Path(__file__).parent.parent / "supabase" / "reduce_vector_embeddings.sql"
    
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
    logger.info("\nTo reduce vector embeddings size, follow these steps:")
    logger.info("1. In the SQL Editor, click 'New query'")
    logger.info("2. Copy and paste the contents of reduce_vector_embeddings.sql into the editor")
    logger.info("3. Review the script and uncomment any additional options if needed")
    logger.info("4. Click 'Run' to execute the SQL")
    logger.info("\nWARNING: This script provides three options for reducing database size:")
    logger.info("- Option 1 (Enabled by default): Drop embedding indexes but keep the data")
    logger.info("- Option 2 (Commented out): Remove embedding columns completely")
    logger.info("- Option 3 (Partially enabled): Delete specific framework_docs rows")
    logger.info("\nReview the script carefully before running it to ensure you're comfortable with the changes.")
    
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
    logger.info("Opening Supabase SQL Editor with vector embeddings reduction script...")
    
    success = open_supabase_sql_editor()
    
    if success:
        logger.info("Supabase SQL Editor opened successfully.")
    else:
        logger.error("Failed to open Supabase SQL Editor.")

if __name__ == "__main__":
    main()
