#!/usr/bin/env python3
"""
Enhanced Job Search Module for Climate Economy Ecosystem

This module extends the existing job search functionality to leverage
user profile enrichment data for better job matches and recommendations.
It ensures that only member companies are included in search results.

Usage:
    from enhanced_job_search import search_jobs_for_user, get_job_recommendations
"""

import os
import sys
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.job_search import JobSearchTool
from tools.profile_enrichment import ProfileEnricher
from lib.monitoring.metrics_service import metrics_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enhanced_job_search.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Serper API configuration for real-time job listings
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = "https://google.serper.dev/search"

class EnhancedJobSearch:
    """Enhanced job search tool that leverages profile enrichment data."""
    
    def __init__(self):
        """Initialize the enhanced job search tool."""
        self.job_search_tool = JobSearchTool()
        self.profile_enricher = ProfileEnricher()
        self.api_key = SERPER_API_KEY
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Validation
        if not self.api_key:
            logger.error("Cannot initialize EnhancedJobSearch: Serper API key not available")
    
    async def search_jobs_for_user(self, 
                                  user_profile: Dict[str, Any], 
                                  search_params: Dict[str, Any],
                                  member_companies_only: bool = True) -> Dict[str, Any]:
        """
        Search for jobs based on user profile and search parameters.
        
        Args:
            user_profile: User profile data
            search_params: Search parameters
            member_companies_only: Whether to only include results from member companies
            
        Returns:
            Dict with search results
        """
        start_time = time.time()
        
        try:
            # Extract parameters
            query = search_params.get("query", "")
            sectors = search_params.get("sectors", [])
            focus_areas = search_params.get("focus_areas", [])
            locations = search_params.get("locations", [])
            skills = search_params.get("skills", [])
            experience_level = search_params.get("experience_level", "")
            remote_status = search_params.get("remote_status", "any")
            
            # Enhanced search parameters
            enhanced_params = await self._enhance_search_parameters(
                user_profile, 
                query, 
                skills,
                sectors,
                focus_areas
            )
            
            # Combine original and enhanced parameters
            search_text = enhanced_params.get("search_text", query)
            enhanced_skills = enhanced_params.get("skills", skills)
            
            # Perform job search
            job_results = await self._search_real_time_jobs(
                search_text=search_text,
                locations=locations,
                skills=enhanced_skills
            )
            
            # Filter for member companies if needed
            if member_companies_only:
                job_results = self._filter_member_companies(job_results)
            
            # Calculate relevance scores based on user profile
            scored_results = self._calculate_relevance_scores(job_results, user_profile)
            
            # Sort by relevance score
            sorted_results = sorted(
                scored_results, 
                key=lambda x: x.get("relevance_score", 0), 
                reverse=True
            )
            
            # Track metrics
            end_time = time.time()
            user_id = user_profile.get("id", "unknown")
            
            # Log search analytics to database
            self._log_search_analytics(
                user_id=user_id,
                search_query=search_text,
                search_type="enhanced",
                result_count=len(sorted_results),
                search_params={
                    "original_query": query,
                    "enhanced_query": search_text,
                    "locations": locations,
                    "skills": enhanced_skills,
                    "sectors": sectors,
                    "focus_areas": focus_areas,
                    "remote_status": remote_status,
                    "experience_level": experience_level
                }
            )
            
            # Track metrics with metrics service
            if metrics_service:
                await metrics_service.track_enhanced_job_search(
                    user_id=user_id,
                    search_data={
                        "query": search_text,
                        "results": sorted_results,
                        "used_profile_data": bool(enhanced_params.get("used_profile", False)),
                        "sectors": sectors,
                        "skills": enhanced_skills,
                        "is_recommendation": False,
                        "performance": {
                            "duration_ms": int((end_time - start_time) * 1000)
                        }
                    }
                )
            
            return {
                "jobs": sorted_results,
                "search_stats": {
                    "total_results": len(sorted_results),
                    "search_text": search_text,
                    "enhanced": enhanced_params.get("used_profile", False),
                    "duration_ms": int((end_time - start_time) * 1000)
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching jobs for user: {str(e)}")
            return {
                "jobs": [],
                "error": str(e)
            }
    
    async def _enhance_search_parameters(self, 
                                       user_profile: Dict[str, Any], 
                                       search_text: str, 
                                       skills: List[str],
                                       sectors: List[str],
                                       focus_areas: List[str]) -> Dict[str, Any]:
        """
        Enhance search parameters using profile enrichment data.
        
        Args:
            user_profile: User profile data
            search_text: Original search text
            skills: Original skills list
            sectors: Original sectors list
            focus_areas: Original focus areas list
            
        Returns:
            Dict with enhanced search parameters
        """
        enhanced_params = {
            "search_text": search_text,
            "skills": skills.copy() if skills else [],
            "sectors": sectors.copy() if sectors else [],
            "focus_areas": focus_areas.copy() if focus_areas else []
        }
        
        # Check if profile has enrichment data
        if "enrichment" in user_profile and user_profile["enrichment"].get("status") == "completed":
            enrichment = user_profile["enrichment"]
            
            # Add technical skills from enrichment
            if "skills" in enrichment and "technical" in enrichment["skills"]:
                technical_skills = enrichment["skills"]["technical"]
                for skill in technical_skills:
                    if skill not in enhanced_params["skills"]:
                        enhanced_params["skills"].append(skill)
            
            # Add transferable skills from enrichment
            if "skills" in enrichment and "transferable" in enrichment["skills"]:
                transferable_skills = enrichment["skills"]["transferable"]
                for skill in transferable_skills:
                    if skill not in enhanced_params["skills"]:
                        enhanced_params["skills"].append(skill)
            
            # Expand search text with key skills if the original is empty or very short
            if not search_text or len(search_text.strip()) < 3:
                # Build better search text from top skills
                all_skills = []
                if "skills" in enrichment:
                    all_skills.extend(enrichment["skills"].get("technical", []))
                    all_skills.extend(enrichment["skills"].get("transferable", []))
                
                if all_skills:
                    # Use top 3 skills for search text
                    top_skills = all_skills[:3]
                    enhanced_params["search_text"] = " ".join(top_skills)
        
        # Add user interests if available
        if "interests" in user_profile:
            interests = user_profile["interests"]
            if isinstance(interests, list):
                for interest in interests:
                    if interest not in enhanced_params["focus_areas"]:
                        enhanced_params["focus_areas"].append(interest)
        
        return enhanced_params
    
    async def _search_real_time_jobs(self, search_text: str, locations: List[str], skills: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for real-time job listings using Serper API.
        
        Args:
            search_text: Search query text
            locations: List of locations to search in
            skills: List of skills to include in search
            
        Returns:
            List of job listings
        """
        # Build search query
        location_str = " OR ".join(locations) if locations else "Massachusetts"
        skills_str = " OR ".join(skills[:5]) if skills else ""  # Limit to top 5 skills
        
        # Combine into search query
        if skills_str:
            query = f"{search_text} ({skills_str}) jobs in {location_str}"
        else:
            query = f"{search_text} jobs in {location_str}"
        
        query += " clean energy climate"  # Add domain-specific terms
        
        try:
            logger.info(f"Performing real-time job search: {query}")
            
            # Build the API request
            payload = {
                "q": query,
                "gl": "us",
                "hl": "en",
                "num": 20  # Number of results to return
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SERPER_API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"API error: {response.status_code}, {response.text}")
                    return []
                
                # Parse response
                search_data = response.json()
                
                # Extract job listings
                return self._extract_job_listings(search_data, search_text)
                
        except Exception as e:
            logger.error(f"Error during real-time job search: {str(e)}")
            return []
    
    def _extract_job_listings(self, search_data: Dict[str, Any], search_text: str) -> List[Dict[str, Any]]:
        """
        Extract job listings from search results.
        
        Args:
            search_data: Search result data
            search_text: Original search query
            
        Returns:
            List of job listings
        """
        job_listings = []
        
        try:
            # Process organic search results
            organic_results = search_data.get("organic", [])
            
            for result in organic_results:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                # Skip if not likely a job listing
                if not any(job_term in title.lower() for job_term in ["job", "career", "position", "hiring", "opening"]):
                    continue
                
                # Extract company name (best guess)
                company = self._extract_company_name(title, snippet)
                
                # Extract location (best guess)
                location = self._extract_location(title, snippet)
                
                # Create job listing entry
                job_listing = {
                    "id": f"rt_{hash(link)}",  # Generate ID from link hash
                    "title": title.replace(" - job posting", "").replace(" - Job", ""),
                    "company": company,
                    "description": snippet,
                    "requirements": "",  # Not available in search results
                    "location": location or "Massachusetts",
                    "application_url": link,
                    "posted_date": self._get_current_date(),
                    "source": "real-time-search",
                    "search_text": search_text
                }
                
                job_listings.append(job_listing)
            
            return job_listings
            
        except Exception as e:
            logger.error(f"Error extracting job listings: {str(e)}")
            return []
    
    def _extract_company_name(self, title: str, snippet: str) -> str:
        """Extract company name from job title and snippet."""
        import re
        
        # Common patterns for company names in job titles
        patterns = [
            r"at ([A-Za-z0-9 &\.]+)",  # "Job Title at Company"
            r"with ([A-Za-z0-9 &\.]+)",  # "Job Title with Company"
            r"- ([A-Za-z0-9 &\.]+)",  # "Job Title - Company"
            r"\| ([A-Za-z0-9 &\.]+)",  # "Job Title | Company"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1).strip()
        
        # If no match in title, try to extract from snippet
        match = re.search(r"([A-Za-z0-9 &\.]+) is hiring", snippet)
        if match:
            return match.group(1).strip()
        
        return "Unknown Company"
    
    def _extract_location(self, title: str, snippet: str) -> Optional[str]:
        """Extract location from job title and snippet."""
        import re
        
        # Combined text for searching
        text = f"{title} {snippet}"
        
        # Look for Massachusetts cities
        ma_cities = [
            "Boston", "Worcester", "Springfield", "Cambridge", "Lowell", 
            "Brockton", "New Bedford", "Lynn", "Quincy", "Newton",
            "Somerville", "Framingham", "Lawrence", "Haverhill", "Waltham",
            "Malden", "Brookline", "Plymouth", "Medford", "Taunton",
            "Chicopee", "Weymouth", "Revere", "Peabody", "Methuen"
        ]
        
        for city in ma_cities:
            if re.search(rf"\b{city}\b", text, re.IGNORECASE):
                return f"{city}, MA"
        
        # Look for Massachusetts abbreviation
        if re.search(r"\bMA\b", text) or "Massachusetts" in text:
            return "Massachusetts"
        
        return None
    
    def _get_current_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.utcnow().date().isoformat()
    
    def _filter_member_companies(self, job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter job listings to only include member companies.
        
        Args:
            job_listings: List of job listings
            
        Returns:
            Filtered list of job listings
        """
        # Get member company names from the job search tool
        from constants import ACT_COMPANY_NAMES
        
        if not ACT_COMPANY_NAMES:
            logger.warning("No member companies defined, returning all listings")
            return job_listings
        
        member_companies = [name.lower() for name in ACT_COMPANY_NAMES]
        
        # Filter job listings
        filtered_listings = []
        for job in job_listings:
            company = job.get("company", "").lower()
            
            # Check if this company is a member
            if any(member.lower() in company or company in member.lower() for member in member_companies):
                filtered_listings.append(job)
        
        logger.info(f"Filtered {len(job_listings)} job listings to {len(filtered_listings)} member company listings")
        return filtered_listings
    
    def _merge_job_results(self, existing_results: List[Dict[str, Any]], new_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge job results avoiding duplicates.
        
        Args:
            existing_results: Existing job results
            new_results: New job results to merge
            
        Returns:
            Merged list of job results
        """
        merged = existing_results.copy()
        existing_ids = {job.get("id") for job in existing_results}
        existing_titles = {job.get("title").lower() for job in existing_results if job.get("title")}
        
        # Add new results that don't duplicate existing ones
        for job in new_results:
            job_id = job.get("id")
            job_title = job.get("title", "").lower()
            
            # Skip if ID already exists
            if job_id in existing_ids:
                continue
                
            # Skip if very similar title already exists
            title_match = False
            for existing_title in existing_titles:
                if self._is_similar_title(job_title, existing_title):
                    title_match = True
                    break
            
            if not title_match:
                merged.append(job)
                existing_ids.add(job_id)
                existing_titles.add(job_title)
        
        return merged
    
    def _is_similar_title(self, title1: str, title2: str) -> bool:
        """Check if two job titles are very similar."""
        # Simple check based on shared words
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        # Calculate overlap
        overlap = words1.intersection(words2)
        
        # If more than 60% of words match, consider similar
        if len(overlap) >= 0.6 * min(len(words1), len(words2)):
            return True
            
        return False
    
    def _calculate_relevance_scores(self, job_results: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate relevance scores for job results based on user profile.
        
        Args:
            job_results: List of job results
            user_profile: User profile data
            
        Returns:
            Job results with relevance scores
        """
        scored_results = []
        
        # Extract user skills
        user_skills = set()
        
        # Regular profile skills
        if "skills" in user_profile and isinstance(user_profile["skills"], list):
            user_skills.update([s.lower() for s in user_profile["skills"]])
        
        # Enriched profile skills
        if "enrichment" in user_profile and "skills" in user_profile["enrichment"]:
            enriched_skills = user_profile["enrichment"]["skills"]
            if "technical" in enriched_skills:
                user_skills.update([s.lower() for s in enriched_skills["technical"]])
            if "transferable" in enriched_skills:
                user_skills.update([s.lower() for s in enriched_skills["transferable"]])
            if "soft" in enriched_skills:
                user_skills.update([s.lower() for s in enriched_skills["soft"]])
        
        # User interests
        user_interests = set()
        if "interested_sectors" in user_profile:
            user_interests.update([s.lower() for s in user_profile["interested_sectors"]])
        if "interested_focus_areas" in user_profile:
            user_interests.update([s.lower() for s in user_profile["interested_focus_areas"]])
        
        # User location preferences
        user_locations = set()
        if "preferred_locations" in user_profile:
            user_locations.update([l.lower() for l in user_profile["preferred_locations"]])
        
        # Calculate score for each job
        for job in job_results:
            # Start with base score
            score = 50.0
            
            # Extract job skills
            job_skills = set()
            if "skills_required" in job and isinstance(job["skills_required"], list):
                job_skills.update([s.lower() for s in job["skills_required"]])
            
            # Extract from job description and title
            job_text = f"{job.get('title', '')} {job.get('description', '')}"
            job_text_lower = job_text.lower()
            
            # Skill match score (up to 30 points)
            skill_matches = 0
            for skill in user_skills:
                if skill in job_text_lower or any(s in skill for s in job_skills):
                    skill_matches += 1
            
            skill_score = min(30, skill_matches * 5)
            score += skill_score
            
            # Interest match score (up to 10 points)
            interest_matches = 0
            for interest in user_interests:
                if interest in job_text_lower:
                    interest_matches += 1
            
            interest_score = min(10, interest_matches * 2)
            score += interest_score
            
            # Location match score (up to 10 points)
            location_score = 0
            job_location = job.get("location", "").lower()
            
            if user_locations and any(loc in job_location or job_location in loc for loc in user_locations):
                location_score = 10
            elif not user_locations and "ma" in job_location or "massachusetts" in job_location:
                # Default to Massachusetts if no location preferences
                location_score = 5
            
            score += location_score
            
            # Add the score to the job
            scored_job = job.copy()
            scored_job["relevance_score"] = score
            scored_job["skill_match"] = skill_matches
            scored_job["interest_match"] = interest_matches
            scored_job["location_match"] = bool(location_score)
            
            scored_results.append(scored_job)
        
        return scored_results
    
    async def get_job_recommendations(self, user_profile: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get job recommendations based on user profile.
        
        Args:
            user_profile: User profile data
            limit: Maximum number of recommendations to return
            
        Returns:
            List of job recommendations
        """
        start_time = time.time()
        
        try:
            # Build search parameters from user profile
            search_params = {
                "query": "",
                "sectors": [],
                "focus_areas": [],
                "locations": [],
                "skills": [],
                "experience_level": "",
                "remote_status": "any"
            }
            
            # Extract interests from profile
            if user_profile.get("interests"):
                search_params["query"] = " ".join(user_profile.get("interests", []))
                search_params["sectors"] = user_profile.get("interests", [])[:3]
            
            # Extract skills from enriched profile
            if user_profile.get("enrichment") and user_profile["enrichment"].get("skills"):
                skills = user_profile["enrichment"]["skills"]
                technical_skills = skills.get("technical", [])
                transferable_skills = skills.get("transferable", [])
                
                # Use top technical and transferable skills
                top_skills = technical_skills[:5] + transferable_skills[:3]
                search_params["skills"] = top_skills
            
            # Extract preferred locations
            if user_profile.get("preferred_locations"):
                search_params["locations"] = user_profile.get("preferred_locations", [])
            
            # Search for jobs using these parameters
            results = await self.search_jobs_for_user(
                user_profile=user_profile,
                search_params=search_params,
                member_companies_only=True
            )
            
            # Get top recommendations
            recommendations = results.get("jobs", [])[:limit]
            
            # Track metrics
            end_time = time.time()
            user_id = user_profile.get("id", "unknown")
            
            # Log recommendation analytics
            self._log_search_analytics(
                user_id=user_id,
                search_query="job_recommendations",
                search_type="recommendation",
                result_count=len(recommendations),
                search_params=search_params
            )
            
            # Track metrics with metrics service
            if metrics_service:
                await metrics_service.track_enhanced_job_search(
                    user_id=user_id,
                    search_data={
                        "query": "recommendations",
                        "results": recommendations,
                        "used_profile_data": True,
                        "sectors": search_params["sectors"],
                        "skills": search_params["skills"],
                        "is_recommendation": True,
                        "performance": {
                            "duration_ms": int((end_time - start_time) * 1000)
                        }
                    }
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {str(e)}")
            return []

    def _log_search_analytics(self, user_id: str, search_query: str, search_type: str, 
                             result_count: int, search_params: Dict[str, Any]) -> None:
        """
        Log search analytics to the database.
        
        Args:
            user_id: User ID
            search_query: Search query text
            search_type: Type of search (enhanced or recommendation)
            result_count: Number of results
            search_params: Search parameters
        """
        try:
            supabase = self._get_supabase_client()
            if not supabase:
                return
            
            supabase.table("search_analytics").insert({
                "user_id": user_id,
                "search_query": search_query[:255] if search_query else "",  # Limit string length
                "search_type": search_type,
                "result_count": result_count,
                "search_params": search_params
            }).execute()
            
        except Exception as e:
            logger.error(f"Error logging search analytics: {str(e)}")

# Create singleton instance
enhanced_job_search = EnhancedJobSearch()

async def search_jobs_for_user(user_profile: Dict[str, Any], search_params: Dict[str, Any], member_companies_only: bool = True) -> Dict[str, Any]:
    """
    Search for jobs based on user profile and search parameters.
    
    Args:
        user_profile: User profile data
        search_params: Search parameters
        member_companies_only: Whether to restrict results to member companies
        
    Returns:
        Dict with search results
    """
    return await enhanced_job_search.search_jobs_for_user(user_profile, search_params, member_companies_only)

async def get_job_recommendations(user_profile: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get job recommendations for a user based on their profile.
    
    Args:
        user_profile: User profile data
        limit: Maximum number of recommendations to return
        
    Returns:
        List of job recommendations
    """
    return await enhanced_job_search.get_job_recommendations(user_profile, limit)

if __name__ == "__main__":
    import sys
    import json
    
    async def main():
        try:
            # Get user profile and search params from command line
            if len(sys.argv) < 2:
                print("Please provide user profile and search params JSON", file=sys.stderr)
                sys.exit(1)
            
            # Parse user profile
            user_profile = json.loads(sys.argv[1])
            
            # Parse search params if provided
            search_params = {}
            if len(sys.argv) > 2:
                search_params = json.loads(sys.argv[2])
            
            # Get function to call
            func_name = sys.argv[3] if len(sys.argv) > 3 else "search"
            
            if func_name == "search":
                # Search for jobs
                results = await search_jobs_for_user(user_profile, search_params)
            else:
                # Get recommendations
                limit = int(search_params.get("limit", 10))
                results = await get_job_recommendations(user_profile, limit)
            
            # Print results as JSON
            print(json.dumps(results))
            
        except Exception as e:
            print(json.dumps({
                "error": str(e),
                "jobs": [],
                "count": 0
            }))
            sys.exit(1)
    
    # Run main function
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main()) 