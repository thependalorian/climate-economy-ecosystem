#!/usr/bin/env python3
"""
List Supabase Tables and Embeddings

This script lists all tables and embeddings in the Supabase database.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import json

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

def list_supabase_tables_and_embeddings():
    """List all tables and embeddings in the Supabase database."""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials not found in environment variables.")
        return

    try:
        # Import Supabase client
        from supabase.client import create_client, Client

        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # List all tables
        logger.info("Checking for common tables...")

        # Try common tables that we expect to exist
        common_tables = [
            'profiles', 'resumes', 'resume_analysis', 'job_recommendations',
            'skill_gaps', 'training_paths', 'chats', 'chat_messages',
            'memories', 'chat_feedback', 'profile_enrichment', 'user_engagement',
            'feature_votes', 'connection_thresholds', 'reasoning_steps', 'documents'
        ]

        existing_tables = []
        for table in common_tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                if hasattr(response, 'data'):
                    existing_tables.append(table)
                    logger.info(f"Table '{table}' exists with {len(response.data)} sample rows.")
            except Exception as e:
                logger.info(f"Table '{table}' does not exist or error: {str(e)[:100]}...")

        logger.info(f"\nFound {len(existing_tables)} existing tables: {', '.join(existing_tables)}")

        # Check for vector columns in existing tables
        logger.info("\nChecking for vector columns...")

        for table in existing_tables:
            try:
                # Try to get a sample row to examine its structure
                sample = supabase.table(table).select('*').limit(1).execute()

                if hasattr(sample, 'data') and sample.data:
                    # Check each column to see if it might be a vector
                    for col, value in sample.data[0].items():
                        if isinstance(value, list) and len(value) > 10:  # Heuristic for vector
                            logger.info(f"Table '{table}' column '{col}' might be a vector with dimension: {len(value)}")
            except Exception as e:
                logger.warning(f"Could not check vector columns for table '{table}': {str(e)[:100]}...")
    except Exception as e:
        logger.error(f"Error listing tables and embeddings: {e}")

if __name__ == "__main__":
    list_supabase_tables_and_embeddings()
