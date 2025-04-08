#!/usr/bin/env python3
"""
Remove NextJS Framework Docs

This script removes NextJS framework-related rows from the framework_docs table
to reduce the database size.
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

def get_table_size(supabase, table_name):
    """Get the size of a table in MB."""
    try:
        # Use a custom query to get the table size
        response = supabase.rpc(
            'get_table_size',
            {'table_name': table_name}
        ).execute()
        
        if hasattr(response, 'data') and response.data:
            # Size is returned in bytes, convert to MB
            size_mb = response.data[0]['size_mb'] if 'size_mb' in response.data[0] else 0
            return size_mb
        
        logger.warning(f"Could not get size for table {table_name}. Using alternative method.")
        
        # Alternative method: count rows and estimate size
        count_response = supabase.table(table_name).select('*', count='exact').execute()
        if hasattr(count_response, 'count'):
            # Rough estimate: 5KB per row
            estimated_size_mb = (count_response.count * 5) / 1024
            logger.info(f"Estimated size of {table_name}: {estimated_size_mb:.2f} MB (based on {count_response.count} rows)")
            return estimated_size_mb
        
        return 0
    except Exception as e:
        logger.error(f"Error getting size for table {table_name}: {e}")
        return 0

def remove_nextjs_framework_docs(supabase):
    """
    Remove NextJS framework-related rows from the framework_docs table.
    
    Args:
        supabase: Supabase client
    """
    logger.info("Removing NextJS framework-related rows from framework_docs table...")
    
    try:
        # Get the current size of the framework_docs table
        initial_size = get_table_size(supabase, 'framework_docs')
        logger.info(f"Current size of framework_docs table: {initial_size:.2f} MB")
        
        # Search for NextJS-related rows
        nextjs_keywords = [
            'next.js', 
            'nextjs', 
            'next-js', 
            'vercel', 
            'react server component',
            'app router',
            'pages router',
            'next/router',
            'next/link',
            'next/image',
            'next/head',
            'next/script',
            'next/font',
            'next/dynamic',
            'getStaticProps',
            'getServerSideProps',
            'getInitialProps',
            'useRouter',
            'createNextContext'
        ]
        
        total_deleted = 0
        
        for keyword in nextjs_keywords:
            logger.info(f"Searching for rows containing '{keyword}'...")
            
            # Search for rows containing the keyword
            response = supabase.table('framework_docs').select('id, title').ilike('content', f'%{keyword}%').execute()
            
            if not hasattr(response, 'data') or not response.data:
                logger.info(f"No rows found containing '{keyword}'.")
                continue
            
            rows = response.data
            logger.info(f"Found {len(rows)} rows containing '{keyword}'.")
            
            # Delete the rows in batches to avoid timeouts
            batch_size = 10
            deleted_count = 0
            
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                ids = [row['id'] for row in batch]
                
                # Delete the rows
                delete_response = supabase.table('framework_docs').delete().in_('id', ids).execute()
                
                if hasattr(delete_response, 'data'):
                    deleted_count += len(delete_response.data)
                    logger.info(f"Deleted batch of {len(delete_response.data)} rows. Total deleted for '{keyword}': {deleted_count}")
                
                # Sleep briefly to avoid rate limits
                time.sleep(1)
            
            total_deleted += deleted_count
        
        # Get the new size of the framework_docs table
        final_size = get_table_size(supabase, 'framework_docs')
        logger.info(f"New size of framework_docs table: {final_size:.2f} MB")
        logger.info(f"Reduced by: {initial_size - final_size:.2f} MB")
        
        logger.info(f"Successfully deleted {total_deleted} NextJS framework-related rows from framework_docs table.")
        return True
    except Exception as e:
        logger.error(f"Error removing NextJS framework-related rows: {e}")
        return False

def main():
    """Main function to remove NextJS framework-related rows."""
    logger.info("Starting removal of NextJS framework-related rows...")
    
    # Connect to Supabase
    supabase = connect_to_supabase()
    if not supabase:
        logger.error("Failed to connect to Supabase. Exiting...")
        return
    
    # Remove NextJS framework-related rows
    success = remove_nextjs_framework_docs(supabase)
    
    if success:
        logger.info("Successfully removed NextJS framework-related rows.")
    else:
        logger.warning("Failed to remove NextJS framework-related rows.")
    
    logger.info("Removal of NextJS framework-related rows completed.")

if __name__ == "__main__":
    main()
