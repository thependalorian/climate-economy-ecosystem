#!/usr/bin/env python3
"""
Job Search API Script for Massachusetts Climate Economy Assistant

This script is called by the job search API endpoint to search for jobs
using our job search tool. It takes search parameters as JSON and returns
search results as JSON.

Usage:
    python job_search_api.py '{"user_id": "123", "search_text": "energy"}'
"""

import os
import sys
import json
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.job_search import search_jobs_for_user
from constants import ACT_COMPANY_NAMES

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
    handlers=[
        logging.FileHandler('job_search_api.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    logger.error("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
    sys.exit(1)

try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    sys.exit(1)

def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Get user profile from Supabase.
    
    Args:
        user_id: User ID
        
    Returns:
        User profile data
    """
    try:
        result = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        # If no profile found, return basic profile
        return {
            "id": user_id,
            "name": "User",
            "email": "",
            "skills": [],
            "interested_sectors": [],
            "interested_focus_areas": []
        }
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        # Return basic profile
        return {
            "id": user_id,
            "name": "User",
            "email": "",
            "skills": [],
            "interested_sectors": [],
            "interested_focus_areas": []
        }

def run_job_search(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run job search based on parameters.
    
    Args:
        params: Search parameters
        
    Returns:
        Search results
    """
    try:
        # Extract parameters
        user_id = params.get("user_id")
        search_text = params.get("search_text")
        sectors = params.get("sectors", [])
        focus_areas = params.get("focus_areas", [])
        locations = params.get("locations", [])
        skills = params.get("skills", [])
        experience_level = params.get("experience_level")
        remote_status = params.get("remote_status")
        use_cache = params.get("use_cache", True)
        
        # Get user profile
        user_profile = get_user_profile(user_id)
        
        # Merge explicit skills with profile skills if not provided
        if not skills and user_profile.get("skills"):
            skills = user_profile.get("skills")
        
        # Merge explicit sectors with profile sectors if not provided
        if not sectors and user_profile.get("interested_sectors"):
            sectors = user_profile.get("interested_sectors")
        
        # Merge explicit focus areas with profile focus areas if not provided
        if not focus_areas and user_profile.get("interested_focus_areas"):
            focus_areas = user_profile.get("interested_focus_areas")
        
        # Search for jobs
        results = search_jobs_for_user(
            user_profile=user_profile,
            search_text=search_text,
            sectors=sectors,
            focus_areas=focus_areas,
            locations=locations,
            skills=skills,
            experience_level=experience_level,
            remote_status=remote_status,
            use_cache=use_cache
        )
        
        # Log search
        logger.info(f"Job search for user {user_id}: {len(results)} results found")
        
        # Format results for API
        formatted_results = []
        for job in results:
            # Only include jobs from our defined companies
            if job.get("company") in ACT_COMPANY_NAMES:
                formatted_job = {
                    "id": str(job.get("id")),
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "description": job.get("description", ""),
                    "requirements": job.get("requirements", ""),
                    "location": job.get("location", ""),
                    "sector": job.get("sector", ""),
                    "focus_areas": job.get("focus_areas", []),
                    "skills_required": job.get("skills_required", []),
                    "experience_level": job.get("experience_level", ""),
                    "remote_status": job.get("remote_status", ""),
                    "application_url": job.get("application_url", ""),
                    "posted_date": job.get("posted_date", "")
                }
                formatted_results.append(formatted_job)
        
        return {
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results),
            "query": {
                "search_text": search_text,
                "sectors": sectors,
                "focus_areas": focus_areas,
                "locations": locations,
                "skills": skills,
                "experience_level": experience_level,
                "remote_status": remote_status
            }
        }
        
    except Exception as e:
        logger.error(f"Error running job search: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "results": [],
            "count": 0
        }

if __name__ == "__main__":
    try:
        # Get parameters from command line
        if len(sys.argv) < 2:
            logger.error("No parameters provided")
            sys.exit(1)
        
        # Parse parameters
        params = json.loads(sys.argv[1])
        
        # Run job search
        results = run_job_search(params)
        
        # Print results as JSON
        print(json.dumps(results))
        
    except Exception as e:
        # Print error as JSON
        print(json.dumps({
            "success": False,
            "error": str(e),
            "results": [],
            "count": 0
        })) 