#!/usr/bin/env python3
"""
Reduce Database Size Script

This script reduces the size of the Supabase database by selectively removing
data from the largest tables to bring the database size under the free plan limit.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def connect_to_supabase():
    """Connect to Supabase."""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not found in environment variables.")
        return None
    
    try:
        # Import Supabase client
        from supabase.client import create_client, Client
        
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Successfully connected to Supabase!")
        return supabase
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {e}")
        return None

def get_table_row_count(supabase, table_name):
    """Get the number of rows in a table."""
    try:
        # Use count() to get the number of rows
        response = supabase.table(table_name).select('*', count='exact').execute()
        if hasattr(response, 'count'):
            return response.count
        return 0
    except Exception as e:
        logger.error(f"Error getting row count for table {table_name}: {e}")
        return 0

def reduce_framework_docs_size(supabase, target_reduction_mb=30):
    """
    Reduce the size of the framework_docs table.
    
    Args:
        supabase: Supabase client
        target_reduction_mb: Target reduction in MB
    """
    logger.info(f"Attempting to reduce framework_docs table size by approximately {target_reduction_mb} MB...")
    
    try:
        # Get the total number of rows in the table
        total_rows = get_table_row_count(supabase, 'framework_docs')
        logger.info(f"Total rows in framework_docs: {total_rows}")
        
        if total_rows == 0:
            logger.warning("No rows found in framework_docs table.")
            return False
        
        # Calculate the average size per row (in MB)
        table_size_mb = 386.77  # From the database size report
        avg_row_size_mb = table_size_mb / total_rows
        logger.info(f"Average row size: {avg_row_size_mb:.2f} MB")
        
        # Calculate how many rows to delete
        rows_to_delete = int(target_reduction_mb / avg_row_size_mb)
        logger.info(f"Need to delete approximately {rows_to_delete} rows to free up {target_reduction_mb} MB")
        
        if rows_to_delete <= 0:
            logger.warning("No rows need to be deleted.")
            return False
        
        # Get the oldest rows to delete
        response = supabase.table('framework_docs').select('id, created_at').order('created_at').limit(rows_to_delete).execute()
        
        if not hasattr(response, 'data') or not response.data:
            logger.warning("No rows found to delete.")
            return False
        
        rows_to_delete = response.data
        logger.info(f"Found {len(rows_to_delete)} rows to delete.")
        
        # Delete the rows in batches to avoid timeouts
        batch_size = 10
        deleted_count = 0
        
        for i in range(0, len(rows_to_delete), batch_size):
            batch = rows_to_delete[i:i+batch_size]
            ids = [row['id'] for row in batch]
            
            # Delete the rows
            delete_response = supabase.table('framework_docs').delete().in_('id', ids).execute()
            
            if hasattr(delete_response, 'data'):
                deleted_count += len(delete_response.data)
                logger.info(f"Deleted batch of {len(delete_response.data)} rows. Total deleted: {deleted_count}")
            
            # Sleep briefly to avoid rate limits
            time.sleep(1)
        
        logger.info(f"Successfully deleted {deleted_count} rows from framework_docs table.")
        logger.info(f"Estimated space freed: ~{deleted_count * avg_row_size_mb:.2f} MB")
        
        return True
    except Exception as e:
        logger.error(f"Error reducing framework_docs table size: {e}")
        return False

def vacuum_database(supabase):
    """
    Run VACUUM FULL to reclaim space.
    
    Note: This requires superuser privileges, which may not be available in Supabase.
    """
    logger.info("Attempting to vacuum the database to reclaim space...")
    
    try:
        # Try to run VACUUM FULL
        response = supabase.rpc('vacuum_full').execute()
        logger.info("Successfully vacuumed the database.")
        return True
    except Exception as e:
        logger.warning(f"Could not vacuum the database: {e}")
        logger.info("Note: VACUUM FULL requires superuser privileges, which may not be available in Supabase.")
        return False

def main():
    """Main function to reduce database size."""
    logger.info("Starting database size reduction...")
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        logger.error("Failed to connect to Supabase. Exiting...")
        return
    
    # Reduce framework_docs table size
    success = reduce_framework_docs_size(supabase, target_reduction_mb=30)
    
    if success:
        logger.info("Successfully reduced framework_docs table size.")
    else:
        logger.warning("Failed to reduce framework_docs table size.")
    
    # Try to vacuum the database (may not work without superuser privileges)
    vacuum_database(supabase)
    
    logger.info("Database size reduction completed.")
    logger.info("Note: It may take some time for the size reduction to be reflected in the Supabase dashboard.")

if __name__ == "__main__":
    main()
