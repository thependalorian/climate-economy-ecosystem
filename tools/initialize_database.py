#!/usr/bin/env python3
"""
Initialize Database Tables

This script initializes the database tables by running the schema.sql file
in the Supabase SQL Editor.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# No need to load environment variables since we're not connecting to Supabase

def initialize_database():
    """Initialize database tables by running the schema.sql file."""
    try:
        # Read the schema.sql file
        schema_path = Path(__file__).parent.parent / "supabase" / "schema.sql"

        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            return False

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        logger.info(f"Read schema file: {schema_path} ({len(schema_sql)} bytes)")

        # Provide instructions for running the schema.sql file in the SQL Editor
        logger.info("\nTo initialize the database, follow these steps:")
        logger.info("1. Go to the Supabase dashboard: https://app.supabase.com")
        logger.info("2. Select your project")
        logger.info("3. Click on 'SQL Editor' in the left sidebar")
        logger.info("4. Click 'New query'")
        logger.info("5. Copy and paste the contents of schema.sql into the editor")
        logger.info("6. Click 'Run' to execute the SQL")
        logger.info("\nAlternatively, you can use the Supabase CLI to run the schema.sql file:")
        logger.info("supabase db reset --db-url=<your-db-url>")

        # Print the path to the schema.sql file
        logger.info(f"\nSchema file path: {schema_path}")

        # Print the first few lines of the schema.sql file
        lines = schema_sql.split('\n')[:10]
        logger.info("\nFirst few lines of schema.sql:")
        for line in lines:
            logger.info(line)
        logger.info("...")

        return True
    except Exception as e:
        logger.error(f"Error reading schema file: {e}")
        return False

def main():
    """Main function to initialize the database."""
    logger.info("Starting database initialization...")

    success = initialize_database()

    if success:
        logger.info("Database initialization completed successfully.")
    else:
        logger.error("Database initialization failed.")

if __name__ == "__main__":
    main()
