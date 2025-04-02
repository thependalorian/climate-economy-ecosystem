#!/usr/bin/env python3
"""
Job Search Tool for Massachusetts Climate Economy Assistant

This tool searches for job listings from our defined companies,
filters based on user preferences, and saves results to Supabase
for retrieval by other users with similar interests.

Usage:
    from job_search import search_jobs_for_user, get_company_job_listings
"""

import os
import sys
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    ACT_COMPANIES, 
    ACT_COMPANY_NAMES,
    get_companies_by_sector,
    get_companies_by_focus,
    get_companies_for_audience,
    get_companies_by_skill
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('job_search.log')
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
    logger.info("Successfully initialized Supabase client")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    sys.exit(1)

class JobSearchTool:
    """Tool for searching jobs from our defined companies."""
    
    def __init__(self):
        """Initialize the job search tool."""
        # Verify companies table exists
        try:
            result = supabase.table("companies").select("count", count="exact").execute()
            logger.info(f"Connected to companies table, found {result.count} companies")
        except Exception as e:
            logger.error(f"Error connecting to companies table: {str(e)}")
            self._create_companies_table()
    
    def _create_companies_table(self):
        """Create the companies table if it doesn't exist."""
        try:
            # Create companies table from ACT_COMPANIES
            logger.info("Creating companies table from ACT_COMPANIES")
            
            # First check if the table exists
            result = supabase.rpc(
                "does_table_exist", 
                {"table_name": "companies"}
            ).execute()
            
            if not result.data or not result.data[0]:
                # Create the table
                sql = """
                CREATE TABLE IF NOT EXISTS public.companies (
                    name TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    description TEXT NOT NULL,
                    location TEXT,
                    sector TEXT,
                    focus_areas TEXT[],
                    audience TEXT[],
                    skill_sets TEXT[],
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                );
                
                -- Enable RLS
                ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
                
                -- Create policy for authenticated users to read
                CREATE POLICY "Authenticated users can read companies"
                ON public.companies
                FOR SELECT
                TO authenticated
                USING (true);
                
                -- Create policy for service roles to manage
                CREATE POLICY "Service role can manage companies"
                ON public.companies
                FOR ALL 
                TO service_role
                USING (true)
                WITH CHECK (true);
                """
                
                result = supabase.rpc("run_sql", {"sql": sql}).execute()
                logger.info("Created companies table")
            
            # Insert or update companies
            for company in ACT_COMPANIES:
                company_data = {
                    "name": company["name"],
                    "url": company["url"],
                    "description": company["description"],
                    "location": company.get("location", "Massachusetts"),
                    "sector": company.get("sector", ""),
                    "focus_areas": company.get("focus_areas", []),
                    "audience": company.get("audience", []),
                    "skill_sets": company.get("skill_sets", [])
                }
                
                result = supabase.table("companies").upsert(company_data).execute()
                logger.info(f"Added/updated company: {company['name']}")
                
            logger.info("Companies table setup complete")
            
        except Exception as e:
            logger.error(f"Error creating companies table: {str(e)}")
            raise
    
    def search_jobs_for_user(self, 
                            user_profile: Dict[str, Any], 
                            search_text: Optional[str] = None,
                            sectors: Optional[List[str]] = None,
                            focus_areas: Optional[List[str]] = None,
                            locations: Optional[List[str]] = None,
                            skills: Optional[List[str]] = None,
                            experience_level: Optional[str] = None,
                            remote_status: Optional[str] = None,
                            max_results: int = 20,
                            use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search for job listings based on user profile and preferences.
        
        Args:
            user_profile: User profile data
            search_text: Optional text search
            sectors: Optional list of sectors to filter by
            focus_areas: Optional list of focus areas to filter by
            locations: Optional list of locations to filter by 
            skills: Optional list of skills to filter by
            experience_level: Optional experience level to filter by
            remote_status: Optional remote status to filter by
            max_results: Maximum number of results to return
            use_cache: Whether to use cached results if available
            
        Returns:
            List of job listings matching the criteria
        """
        try:
            # Construct search query
            search_query = {
                "search_text": search_text,
                "sectors": sectors,
                "focus_areas": focus_areas,
                "locations": locations,
                "skills": skills,
                "experience_level": experience_level,
                "remote_status": remote_status
            }
            
            # Filter out None values
            search_query = {k: v for k, v in search_query.items() if v is not None}
            
            # If using cache, check for existing results
            if use_cache:
                cached_results = self._get_cached_results(search_query)
                if cached_results:
                    logger.info(f"Found cached results for query: {search_query}")
                    return cached_results
            
            # Get relevant companies based on user profile
            relevant_companies = self._get_relevant_companies(user_profile)
            
            # Search for jobs
            results = self._search_jobs(
                search_text=search_text,
                company_names=relevant_companies,
                sectors=sectors,
                focus_areas=focus_areas,
                skills=skills,
                experience_levels=[experience_level] if experience_level else None,
                locations=locations,
                remote_status=remote_status,
                max_results=max_results
            )
            
            # Cache the results
            if results:
                self._cache_search_results(search_query, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    def _get_relevant_companies(self, user_profile: Dict[str, Any]) -> List[str]:
        """
        Get list of companies relevant to the user based on their profile.
        
        Args:
            user_profile: User profile data
            
        Returns:
            List of company names
        """
        relevant_companies = set()
        
        # Get companies relevant to user type if specified
        user_type = user_profile.get("user_type")
        if user_type:
            for company in get_companies_for_audience(user_type):
                relevant_companies.add(company["name"])
        
        # Get companies relevant to sectors if specified
        sectors = user_profile.get("interested_sectors", [])
        for sector in sectors:
            for company in get_companies_by_sector(sector):
                relevant_companies.add(company["name"])
        
        # Get companies relevant to focus areas if specified
        focus_areas = user_profile.get("interested_focus_areas", [])
        for focus in focus_areas:
            for company in get_companies_by_focus(focus):
                relevant_companies.add(company["name"])
        
        # Get companies relevant to skills if specified
        skills = user_profile.get("skills", [])
        for skill in skills:
            for company in get_companies_by_skill(skill):
                relevant_companies.add(company["name"])
        
        # If no relevant companies found, use all ACT companies
        if not relevant_companies:
            return ACT_COMPANY_NAMES
        
        return list(relevant_companies)
    
    def _search_jobs(self,
                    search_text: Optional[str] = None,
                    company_names: Optional[List[str]] = None,
                    sectors: Optional[List[str]] = None,
                    focus_areas: Optional[List[str]] = None,
                    skills: Optional[List[str]] = None,
                    experience_levels: Optional[List[str]] = None,
                    locations: Optional[List[str]] = None,
                    remote_status: Optional[str] = None,
                    max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for job listings based on criteria.
        
        Args:
            search_text: Optional text search
            company_names: Optional list of company names to filter by
            sectors: Optional list of sectors to filter by
            focus_areas: Optional list of focus areas to filter by
            skills: Optional list of skills to filter by
            experience_levels: Optional list of experience levels to filter by
            locations: Optional list of locations to filter by
            remote_status: Optional remote status to filter by
            max_results: Maximum number of results to return
            
        Returns:
            List of job listings matching the criteria
        """
        try:
            # Call the search_job_listings function
            result = supabase.rpc(
                "search_job_listings",
                {
                    "search_text": search_text,
                    "company_names": company_names,
                    "sectors": sectors,
                    "focus_areas": focus_areas,
                    "skills": skills,
                    "experience_levels": experience_levels,
                    "locations": locations,
                    "remote_status": remote_status,
                    "max_results": max_results
                }
            ).execute()
            
            if result.data:
                return result.data
            return []
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    def _get_cached_results(self, search_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get cached search results for a search query if they exist and are not expired.
        
        Args:
            search_query: Search query parameters
            
        Returns:
            List of job listings or empty list if no cache found
        """
        try:
            # Convert search query to JSON string for comparison
            search_query_json = json.dumps(search_query, sort_keys=True)
            
            # Get cached result
            result = supabase.table("job_search_cache").select("*").filter(
                "search_query->>'query'", "eq", search_query_json
            ).filter(
                "expires_at", "gt", datetime.now(timezone.utc).isoformat()
            ).limit(1).execute()
            
            if not result.data:
                return []
            
            # Get the job listings using the result IDs
            cache_record = result.data[0]
            result_ids = cache_record["result_ids"]
            
            if not result_ids:
                return []
            
            # Get the job listings
            result = supabase.table("job_listings").select("*").in_("id", result_ids).execute()
            
            if result.data:
                return result.data
            return []
            
        except Exception as e:
            logger.error(f"Error getting cached results: {str(e)}")
            return []
    
    def _cache_search_results(self, search_query: Dict[str, Any], results: List[Dict[str, Any]]) -> bool:
        """
        Cache search results for future use.
        
        Args:
            search_query: Search query parameters
            results: Job listings from search
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            # Convert search query to JSON string for storage
            search_query_json = json.dumps(search_query, sort_keys=True)
            
            # Get job IDs from results
            result_ids = [job["id"] for job in results]
            
            # Create cache record
            cache_record = {
                "id": str(uuid.uuid4()),
                "search_query": {"query": search_query_json},
                "result_ids": result_ids,
                "search_time": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            }
            
            # Insert into cache
            result = supabase.table("job_search_cache").insert(cache_record).execute()
            
            if result.data:
                logger.info(f"Cached search results for query: {search_query_json}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error caching search results: {str(e)}")
            return False
    
    def get_company_job_listings(self, company_name: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get all job listings for a specific company.
        
        Args:
            company_name: Name of the company
            max_results: Maximum number of results to return
            
        Returns:
            List of job listings for the company
        """
        try:
            # Validate company is in our list
            if company_name not in ACT_COMPANY_NAMES:
                logger.warning(f"Company {company_name} not in our defined list")
                return []
            
            # Get job listings
            result = supabase.table("job_listings").select("*").eq(
                "company", company_name
            ).order(
                "posted_date", desc=True
            ).limit(max_results).execute()
            
            if result.data:
                return result.data
            return []
            
        except Exception as e:
            logger.error(f"Error getting company job listings: {str(e)}")
            return []
    
    def add_job_listing(self, job_data: Dict[str, Any]) -> bool:
        """
        Add a new job listing to the database.
        
        Args:
            job_data: Job listing data
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Validate company is in our list
            company = job_data.get("company")
            if not company or company not in ACT_COMPANY_NAMES:
                logger.warning(f"Company {company} not in our defined list")
                return False
            
            # Validate required fields
            required_fields = ["title", "description", "company"]
            for field in required_fields:
                if field not in job_data:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Add timestamps
            job_data["id"] = job_data.get("id", str(uuid.uuid4()))
            job_data["posted_date"] = job_data.get("posted_date", datetime.now(timezone.utc).isoformat())
            job_data["created_at"] = datetime.now(timezone.utc).isoformat()
            job_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Insert job listing
            result = supabase.table("job_listings").insert(job_data).execute()
            
            if result.data:
                logger.info(f"Added job listing: {job_data['title']} for {job_data['company']}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error adding job listing: {str(e)}")
            return False

# Create singleton instance
job_search = JobSearchTool()

# Export convenience functions
def search_jobs_for_user(user_profile, **kwargs):
    """Search for jobs based on user profile and preferences."""
    return job_search.search_jobs_for_user(user_profile, **kwargs)

def get_company_job_listings(company_name, max_results=50):
    """Get job listings for a specific company."""
    return job_search.get_company_job_listings(company_name, max_results)

def add_job_listing(job_data):
    """Add a new job listing."""
    return job_search.add_job_listing(job_data)

if __name__ == "__main__":
    # Simple test
    user_profile = {
        "user_type": "Veterans",
        "interested_sectors": ["High-Performance Buildings"],
        "skills": ["HVAC Technician", "Building Auditor"]
    }
    
    results = search_jobs_for_user(
        user_profile, 
        search_text="energy efficiency",
        max_results=5
    )
    
    print(f"Found {len(results)} job listings")
    for job in results:
        print(f"{job['title']} - {job['company']}") 