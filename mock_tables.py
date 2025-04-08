#!/usr/bin/env python3
"""
This script implements mock versions of the missing tables for the Streamlit app.
Instead of using actual Supabase tables that require manual setup, this creates 
in-memory implementations that mimic the expected API.
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the utils.py path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UTILS_PATH = os.path.join(SCRIPT_DIR, 'utils.py')

# Create mock implementations
MOCK_IMPLEMENTATION = """
# Mock data stores (in-memory database)
_mock_profiles = []
_mock_job_matches = []
_mock_chats = []
_mock_activity_log = []

# Mock profile functions
def store_user_profile(profile_data):
    """Store user profile in database."""
    try:
        profile_id = str(uuid.uuid4())
        profile = {
            "id": profile_id,
            "user_id": profile_data.get("user_id", str(uuid.uuid4())),
            "email": profile_data.get("email", ""),
            "name": profile_data.get("name", ""),
            "location": profile_data.get("location", ""),
            "user_type": profile_data.get("user_type", ""),
            "is_veteran": profile_data.get("is_veteran", False),
            "is_ej_community": profile_data.get("is_ej_community", False),
            "gateway_city": profile_data.get("gateway_city"),
            "skills": profile_data.get("skills", []),
            "experience_level": profile_data.get("experience_level", ""),
            "preferred_sectors": profile_data.get("preferred_sectors", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        _mock_profiles.append(profile)
        logger.info(f"Profile stored with ID: {profile_id}")
        return profile_id
    except Exception as e:
        logger.error(f"Error storing profile: {str(e)}")
        return None

def get_user_profile(user_id):
    """Retrieve user profile from database."""
    try:
        for profile in _mock_profiles:
            if profile["user_id"] == user_id:
                return profile
        return None
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return None

# Mock job matches functions
def store_job_match(match_data):
    """Store job match in database."""
    try:
        match_id = str(uuid.uuid4())
        match = {
            "id": match_id,
            "user_id": match_data.get("user_id", ""),
            "job_id": match_data.get("job_id"),
            "company_name": match_data.get("company_name", ""),
            "job_title": match_data.get("job_title", ""),
            "match_score": match_data.get("match_score", 0),
            "status": match_data.get("status", "open"),
            "location": match_data.get("location", ""),
            "url": match_data.get("url"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        _mock_job_matches.append(match)
        logger.info(f"Job match stored with ID: {match_id}")
        return match_id
    except Exception as e:
        logger.error(f"Error storing job match: {str(e)}")
        return None

def get_job_matches(user_id, limit=10):
    """Get job matches for a user."""
    try:
        matches = [match for match in _mock_job_matches if match["user_id"] == user_id]
        return matches[:limit]
    except Exception as e:
        logger.error(f"Error retrieving job matches: {str(e)}")
        return []

# Mock chat functions
def store_chat_message(user_id, message, role="user", context=None):
    """Store chat message in database."""
    try:
        message_id = str(uuid.uuid4())
        chat = {
            "id": message_id,
            "user_id": user_id,
            "message": message,
            "role": role,
            "context": context or {},
            "created_at": datetime.now().isoformat()
        }
        _mock_chats.append(chat)
        logger.info(f"Chat message stored with ID: {message_id}")
        return message_id
    except Exception as e:
        logger.error(f"Error storing chat message: {str(e)}")
        return None

def get_chat_history(user_id, limit=50):
    """Get chat history for a user."""
    try:
        chats = [chat for chat in _mock_chats if chat["user_id"] == user_id]
        return sorted(chats, key=lambda x: x["created_at"])[-limit:]
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return []

# Mock activity log functions
def log_user_activity(user_id, action, details=None):
    """Log user activity."""
    try:
        log_id = str(uuid.uuid4())
        log = {
            "id": log_id,
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "created_at": datetime.now().isoformat()
        }
        _mock_activity_log.append(log)
        logger.info(f"Activity logged with ID: {log_id}")
        return log_id
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
        return None

def get_user_activity(user_id, limit=20):
    """Get user activity log."""
    try:
        logs = [log for log in _mock_activity_log if log["user_id"] == user_id]
        return sorted(logs, key=lambda x: x["created_at"])[-limit:]
    except Exception as e:
        logger.error(f"Error retrieving activity log: {str(e)}")
        return []

# Mock feedback functions
def store_feedback(user_id, chat_id, feedback, score=None):
    """Store user feedback."""
    try:
        log_user_activity(user_id, "feedback_submitted", {
            "chat_id": chat_id,
            "feedback": feedback,
            "score": score
        })
        logger.info(f"Feedback stored for chat: {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing feedback: {str(e)}")
        return False

# Mock metrics functions
def get_user_metrics():
    """Get user metrics."""
    try:
        return {
            "total_users": len(set(p["user_id"] for p in _mock_profiles)),
            "active_today": 5,
            "ej_community_users": len([p for p in _mock_profiles if p.get("is_ej_community", False)]),
            "veteran_users": len([p for p in _mock_profiles if p.get("is_veteran", False)])
        }
    except Exception as e:
        logger.error(f"Error retrieving user metrics: {str(e)}")
        return {"total_users": 0, "active_today": 0, "ej_community_users": 0, "veteran_users": 0}

def get_user_distribution():
    """Get user distribution data."""
    try:
        user_types = {}
        for profile in _mock_profiles:
            user_type = profile.get("user_type", "Other")
            user_types[user_type] = user_types.get(user_type, 0) + 1
        
        return [{"type": k, "count": v} for k, v in user_types.items()]
    except Exception as e:
        logger.error(f"Error retrieving user distribution: {str(e)}")
        return []

def get_recent_activity():
    """Get recent activity data."""
    try:
        return sorted(_mock_activity_log, key=lambda x: x["created_at"], reverse=True)[:10]
    except Exception as e:
        logger.error(f"Error retrieving recent activity: {str(e)}")
        return []

# Initialize with sample data
def initialize_mock_data():
    """Initialize mock data stores with sample data."""
    # Sample profiles
    _mock_profiles.extend([
        {
            "id": str(uuid.uuid4()),
            "user_id": "user1",
            "email": "user1@example.com",
            "name": "John Doe",
            "location": "Boston, MA",
            "user_type": "Job Seeker",
            "is_veteran": True,
            "is_ej_community": False,
            "gateway_city": None,
            "skills": ["Solar Energy", "Project Management"],
            "experience_level": "Entry-Level",
            "preferred_sectors": ["Clean Energy", "Energy Efficiency"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user2",
            "email": "user2@example.com",
            "name": "Jane Smith",
            "location": "Worcester, MA",
            "user_type": "EJ Community Member",
            "is_veteran": False,
            "is_ej_community": True,
            "gateway_city": "Worcester",
            "skills": ["Community Organizing", "Energy Auditing"],
            "experience_level": "Mid-Level",
            "preferred_sectors": ["Environmental Justice", "Renewable Energy"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ])
    
    # Sample job matches
    _mock_job_matches.extend([
        {
            "id": str(uuid.uuid4()),
            "user_id": "user1",
            "job_id": str(uuid.uuid4()),
            "company_name": "EcoTech Solutions",
            "job_title": "Solar Panel Installer",
            "match_score": 85,
            "status": "open",
            "location": "Boston, MA",
            "url": "https://example.com/jobs/123",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user2",
            "job_id": str(uuid.uuid4()),
            "company_name": "GreenPath Energy",
            "job_title": "Community Outreach Coordinator",
            "match_score": 92,
            "status": "applied",
            "location": "Worcester, MA",
            "url": "https://example.com/jobs/456",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ])
    
    # Sample chats
    _mock_chats.extend([
        {
            "id": str(uuid.uuid4()),
            "user_id": "user1",
            "message": "Hello, I'm looking for solar energy jobs in Boston.",
            "role": "user",
            "context": {"location": "Boston", "sector": "Solar Energy"},
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user1",
            "message": "I found 5 solar energy jobs in Boston that match your profile. The top match is Solar Panel Installer at EcoTech Solutions with an 85% match to your skills.",
            "role": "assistant",
            "context": {"location": "Boston", "sector": "Solar Energy", "matches": 5},
            "created_at": datetime.now().isoformat()
        }
    ])
    
    # Sample activity logs
    _mock_activity_log.extend([
        {
            "id": str(uuid.uuid4()),
            "user_id": "user1",
            "action": "profile_created",
            "details": {},
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user1",
            "action": "job_match_viewed",
            "details": {"job_id": _mock_job_matches[0]["id"]},
            "created_at": datetime.now().isoformat()
        }
    ])

    logger.info("Initialized mock data stores with sample data")

# Initialize mock data
initialize_mock_data()
"""

def update_utils_file():
    """Update the utils.py file with mock implementations."""
    try:
        # Read current utils.py content
        with open(UTILS_PATH, 'r') as f:
            content = f.read()
        
        # Check if mock implementation already exists
        if "_mock_profiles" in content:
            logger.info("Mock implementation already exists in utils.py")
            return True
        
        # Add mock implementation to the file
        with open(UTILS_PATH, 'a') as f:
            f.write("\n\n# MOCK IMPLEMENTATIONS FOR MISSING TABLES\n")
            f.write(MOCK_IMPLEMENTATION)
        
        logger.info("✅ Successfully updated utils.py with mock implementations")
        return True
    except Exception as e:
        logger.error(f"❌ Error updating utils.py: {str(e)}")
        return False

def create_utils_aliases():
    """Create aliases for utility functions in app.py."""
    try:
        # Find app.py
        APP_PATH = os.path.join(SCRIPT_DIR, 'app.py')
        
        # Read current app.py content
        with open(APP_PATH, 'r') as f:
            content = f.read()
        
        # Check if import section exists and find where to insert our changes
        import_section = content.find("import streamlit as st")
        if import_section == -1:
            logger.error("❌ Could not find import section in app.py")
            return False
        
        # Prepare the new import section with try-except block
        new_import_section = """
import streamlit as st
import pandas as pd
import os
import sys
import json
import uuid
from datetime import datetime

# Setup path to find modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    # Try to import the actual functions
    from utils import (
        store_chat_message,
        get_user_metrics,
        get_user_distribution,
        get_recent_activity,
        process_resume,
        store_user_profile,
        get_job_matches,
        store_feedback,
        log_user_activity,
        get_user_profile,
        get_chat_history
    )
except ImportError as e:
    print(f"ImportError: {e}")
    # If import fails, use mock implementations
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Using mock implementations for missing functions")
    
    # Mock data stores (in-memory)
    _mock_profiles = []
    _mock_job_matches = []
    _mock_chats = []
    _mock_activity_log = []
    
    def store_chat_message(user_id, message, role="user", context=None):
        chat_id = str(uuid.uuid4())
        _mock_chats.append({
            "id": chat_id,
            "user_id": user_id,
            "message": message,
            "role": role,
            "context": context or {},
            "created_at": datetime.now().isoformat()
        })
        return chat_id
    
    def get_user_metrics():
        return {
            "total_users": 25,
            "active_today": 8,
            "ej_community_users": 12,
            "veteran_users": 7
        }
    
    def get_user_distribution():
        return [
            {"type": "Job Seeker", "count": 15},
            {"type": "EJ Community Member", "count": 12},
            {"type": "Veteran", "count": 7},
            {"type": "Student", "count": 5}
        ]
    
    def get_recent_activity():
        return [
            {"user_id": "user1", "action": "profile_updated", "created_at": datetime.now().isoformat()},
            {"user_id": "user2", "action": "job_match_viewed", "created_at": datetime.now().isoformat()},
            {"user_id": "user3", "action": "chat_completed", "created_at": datetime.now().isoformat()}
        ]
    
    def process_resume(resume_text):
        return {
            "skills": ["Solar Energy", "Project Management", "Customer Service"],
            "experience_level": "Entry-Level",
            "suggested_sectors": ["Clean Energy", "Energy Efficiency"]
        }
    
    def store_user_profile(profile_data):
        return str(uuid.uuid4())
    
    def get_job_matches(user_id, limit=10):
        return [
            {
                "company_name": "EcoTech Solutions",
                "job_title": "Solar Panel Installer",
                "match_score": 85,
                "location": "Boston, MA"
            },
            {
                "company_name": "GreenPath Energy",
                "job_title": "Community Outreach Coordinator",
                "match_score": 92,
                "location": "Worcester, MA"
            }
        ]
    
    def store_feedback(user_id, chat_id, feedback, score=None):
        return True
    
    def log_user_activity(user_id, action, details=None):
        return str(uuid.uuid4())
    
    def get_user_profile(user_id):
        return {
            "name": "Test User",
            "location": "Boston, MA",
            "user_type": "Job Seeker",
            "skills": ["Solar Energy", "Project Management"]
        }
    
    def get_chat_history(user_id, limit=50):
        return [
            {"role": "user", "message": "Hello, I'm looking for solar energy jobs in Boston."},
            {"role": "assistant", "message": "I found 5 solar energy jobs in Boston that match your profile."}
        ]
"""
        
        # Replace the import section
        # Find the next import-related line
        next_import_line = content.find("import", import_section + 1)
        if next_import_line != -1:
            # Find the end of the import section (blank line or non-import line)
            end_of_imports = content.find("\n\n", next_import_line)
            if end_of_imports != -1:
                new_content = content[:import_section] + new_import_section + content[end_of_imports:]
            else:
                new_content = content[:import_section] + new_import_section
        else:
            new_content = content[:import_section] + new_import_section + content[import_section + len("import streamlit as st"):]
        
        # Write the updated content back to app.py
        with open(APP_PATH, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Successfully updated app.py with function aliases")
        return True
    except Exception as e:
        logger.error(f"❌ Error updating app.py: {str(e)}")
        return False

def main():
    """Update files to use mock implementations."""
    logger.info("Updating files to use mock implementations...")
    
    # Update utils.py
    utils_updated = update_utils_file()
    
    # Create aliases in app.py
    app_updated = create_utils_aliases()
    
    if utils_updated and app_updated:
        logger.info("✅ Successfully set up mock implementations for missing tables")
        logger.info("🚀 The Streamlit app should now work without Supabase table errors")
    else:
        logger.error("❌ Could not fully set up mock implementations")
        logger.error("Please check the errors above and try again")

if __name__ == "__main__":
    main() 