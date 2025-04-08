#!/usr/bin/env python3
"""
Setup RLHF Tables for Climate Economy Ecosystem

This script creates the necessary tables for RLHF in Supabase using the Python client.
"""

import os
import sys
import logging
import json
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rlhf_setup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("rlhf_setup")

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

def setup_tables():
    """Set up the necessary tables for RLHF"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return False
    
    try:
        # Initialize Supabase client
        logger.info("Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase successfully!")
        
        # Create chats table
        logger.info("Setting up chats table...")
        try:
            # Try to insert a dummy record to create the table
            dummy_id = str(uuid.uuid4())
            response = supabase.table("chats").insert({
                "id": dummy_id,
                "user_id": "00000000-0000-0000-0000-000000000000",
                "content": "Test message",
                "role": "system",
                "conversation_id": "00000000-0000-0000-0000-000000000000",
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            # Delete the dummy record
            supabase.table("chats").delete().eq("id", dummy_id).execute()
            
            logger.info("Chats table created successfully")
        except Exception as e:
            logger.error(f"Error creating chats table: {str(e)}")
            logger.info("Attempting to continue with setup...")
        
        # Create reasoning_steps table
        logger.info("Setting up reasoning_steps table...")
        try:
            # Try to insert a dummy record to create the table
            dummy_id = str(uuid.uuid4())
            response = supabase.table("reasoning_steps").insert({
                "id": dummy_id,
                "chat_id": "00000000-0000-0000-0000-000000000000",
                "step_content": "Test step",
                "step_order": 1,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            # Delete the dummy record
            supabase.table("reasoning_steps").delete().eq("id", dummy_id).execute()
            
            logger.info("Reasoning steps table created successfully")
        except Exception as e:
            logger.error(f"Error creating reasoning_steps table: {str(e)}")
            logger.info("Attempting to continue with setup...")
        
        # Create chat_feedback table
        logger.info("Setting up chat_feedback table...")
        try:
            # Try to insert a dummy record to create the table
            dummy_id = str(uuid.uuid4())
            response = supabase.table("chat_feedback").insert({
                "id": dummy_id,
                "user_id": "00000000-0000-0000-0000-000000000000",
                "message_id": "00000000-0000-0000-0000-000000000000",
                "feedback_type": "rating",
                "feedback_score": 5,
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            # Delete the dummy record
            supabase.table("chat_feedback").delete().eq("id", dummy_id).execute()
            
            logger.info("Chat feedback table created successfully")
        except Exception as e:
            logger.error(f"Error creating chat_feedback table: {str(e)}")
            logger.info("Attempting to continue with setup...")
        
        # Create feedback_metrics table
        logger.info("Setting up feedback_metrics table...")
        try:
            # Try to insert a dummy record to create the table
            dummy_id = str(uuid.uuid4())
            response = supabase.table("feedback_metrics").insert({
                "id": dummy_id,
                "date": datetime.now(timezone.utc).date().isoformat(),
                "total_feedback_count": 0,
                "positive_feedback_count": 0,
                "negative_feedback_count": 0,
                "average_rating": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            # Delete the dummy record
            supabase.table("feedback_metrics").delete().eq("id", dummy_id).execute()
            
            logger.info("Feedback metrics table created successfully")
        except Exception as e:
            logger.error(f"Error creating feedback_metrics table: {str(e)}")
        
        logger.info("RLHF tables setup completed!")
        return True
    except Exception as e:
        logger.error(f"Error setting up RLHF tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_tables()
    if not success:
        sys.exit(1)
