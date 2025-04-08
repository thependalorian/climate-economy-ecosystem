#!/usr/bin/env python3
"""
Profile Enrichment Module for Climate Economy Ecosystem

This module uses the Serper API to search for additional information about users
based on their name, education, experiences, and social links. It enriches user
profiles with transferable skills, technical skills, and soft skills.

Usage:
    from profile_enrichment import enrich_user_profile
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
import re
import httpx
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("profile_enrichment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Serper API configuration
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = "https://google.serper.dev/search"

# Ensure API key is available
if not SERPER_API_KEY:
    logger.error("SERPER_API_KEY environment variable is not set")

class ProfileEnricher:
    """Tool for enriching user profiles with additional information."""
    
    def __init__(self):
        """Initialize the profile enricher."""
        self.api_key = SERPER_API_KEY
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Validation
        if not self.api_key:
            logger.error("Cannot initialize ProfileEnricher: API key not available")
    
    async def enrich_user_profile(self, 
                                 user_profile: Dict[str, Any],
                                 verify_before_save: bool = True,
                                 member_companies_only: bool = True) -> Dict[str, Any]:
        """
        Enrich a user profile with additional information.
        
        Args:
            user_profile: User profile data to enrich
            verify_before_save: Whether to mark enriched data for user verification
            member_companies_only: Whether to restrict job searches to member companies
            
        Returns:
            Enriched user profile
        """
        # Create a copy of the profile to avoid modifying the original
        enriched_profile = user_profile.copy()
        
        # Initialize enrichment data structures if they don't exist
        if "enrichment" not in enriched_profile:
            enriched_profile["enrichment"] = {
                "status": "pending",
                "last_updated": None,
                "data_sources": [],
                "skills": {
                    "transferable": [],
                    "technical": [],
                    "soft": []
                },
                "verified": False
            }
        
        # Extract profile components for search
        name = user_profile.get("name", "")
        education = user_profile.get("education", [])
        experiences = user_profile.get("experience", [])
        social_links = user_profile.get("social_links", {})
        
        # Build search queries
        search_tasks = []
        
        # Name + education search
        if name and education:
            for edu in education:
                institution = edu.get("institution", "")
                degree = edu.get("degree", "")
                field = edu.get("field", "")
                if institution and (degree or field):
                    query = f"{name} {institution} {degree} {field}"
                    search_tasks.append(self.search_web(query, "education"))
        
        # Name + experience search
        if name and experiences:
            for exp in experiences:
                company = exp.get("company", "")
                title = exp.get("title", "")
                if company or title:
                    query = f"{name} {company} {title}"
                    search_tasks.append(self.search_web(query, "experience"))
        
        # Social links search
        if social_links:
            for platform, url in social_links.items():
                if url and self._is_valid_url(url):
                    search_tasks.append(self.search_web(url, f"social_{platform}"))
        
        # If no specific searches, do a general search with the name
        if not search_tasks and name:
            search_tasks.append(self.search_web(name, "general"))
        
        # Run searches in parallel
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process search results
            all_skills = []
            data_sources = []
            
            for result in search_results:
                if isinstance(result, Exception):
                    logger.error(f"Search error: {str(result)}")
                    continue
                
                # Extract skills and add data sources
                if result and "skills" in result:
                    all_skills.extend(result["skills"])
                if result and "source" in result:
                    data_sources.append(result["source"])
            
            # Categorize skills
            categorized_skills = self.categorize_skills(all_skills)
            
            # Update the enriched profile
            enriched_profile["enrichment"]["skills"] = categorized_skills
            enriched_profile["enrichment"]["data_sources"] = data_sources
            enriched_profile["enrichment"]["status"] = "completed"
            enriched_profile["enrichment"]["last_updated"] = self._get_current_timestamp()
            enriched_profile["enrichment"]["verified"] = not verify_before_save
            
            # Add flags for verification if needed
            if verify_before_save:
                enriched_profile["enrichment"]["needs_verification"] = True
                
            logger.info(f"Profile enrichment completed for user: {name}")
        else:
            logger.warning(f"No search tasks created for user: {name}")
            enriched_profile["enrichment"]["status"] = "failed"
            enriched_profile["enrichment"]["error"] = "Insufficient profile data for enrichment"
        
        return enriched_profile
    
    async def search_web(self, query: str, search_type: str) -> Dict[str, Any]:
        """
        Search the web using Serper API.
        
        Args:
            query: Search query string
            search_type: Type of search (education, experience, social_linkedin, etc.)
            
        Returns:
            Dict with search results
        """
        try:
            logger.info(f"Performing {search_type} search: {query}")
            
            # Build the API request
            payload = {
                "q": query,
                "gl": "us",
                "hl": "en",
                "num": 10  # Number of results to return
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
                    return {"error": f"API error: {response.status_code}"}
                
                # Parse response
                search_data = response.json()
                
                # Extract skills from search results
                extracted_skills = self.extract_skills_from_search(search_data, search_type)
                
                # Return results with source information
                return {
                    "source": {
                        "type": search_type,
                        "query": query,
                        "timestamp": self._get_current_timestamp()
                    },
                    "skills": extracted_skills
                }
                
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            return {"error": str(e)}
    
    def extract_skills_from_search(self, search_data: Dict[str, Any], search_type: str) -> List[str]:
        """
        Extract skills from search results.
        
        Args:
            search_data: Search result data
            search_type: Type of search
            
        Returns:
            List of extracted skills
        """
        extracted_skills = []
        
        try:
            # Process organic search results
            organic_results = search_data.get("organic", [])
            
            for result in organic_results:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                # Combine text for analysis
                text = f"{title} {snippet}"
                
                # Extract skills based on search type
                if search_type == "education":
                    # Look for educational qualifications and associated skills
                    edu_skills = self._extract_education_skills(text)
                    extracted_skills.extend(edu_skills)
                    
                elif search_type == "experience":
                    # Look for job roles, responsibilities, and achievements
                    exp_skills = self._extract_experience_skills(text)
                    extracted_skills.extend(exp_skills)
                    
                elif search_type.startswith("social_"):
                    # Extract from social media profiles
                    social_skills = self._extract_social_skills(text)
                    extracted_skills.extend(social_skills)
                    
                else:  # general search
                    # Generic skill extraction
                    general_skills = self._extract_general_skills(text)
                    extracted_skills.extend(general_skills)
            
            # Remove duplicates and normalize
            return self._normalize_skills(extracted_skills)
            
        except Exception as e:
            logger.error(f"Error extracting skills from search: {str(e)}")
            return []
    
    def _extract_education_skills(self, text: str) -> List[str]:
        """Extract skills from education-related text."""
        skills = []
        
        # Look for degree-related keywords
        degree_keywords = [
            "Bachelor", "Master", "PhD", "Doctorate", "BSc", "BA", "MSc", "MA", "MBA",
            "Engineering", "Computer Science", "Data Science", "Sustainability", 
            "Renewable Energy", "Environmental Science"
        ]
        
        for keyword in degree_keywords:
            if keyword.lower() in text.lower():
                skills.append(f"Education in {keyword}")
        
        # Look for specific skills mentioned in educational context
        edu_skill_patterns = [
            r"trained in ([^,.]+)",
            r"studied ([^,.]+)",
            r"specialized in ([^,.]+)",
            r"focus on ([^,.]+)",
            r"concentration in ([^,.]+)"
        ]
        
        for pattern in edu_skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    skills.append(match.group(1).strip())
        
        return skills
    
    def _extract_experience_skills(self, text: str) -> List[str]:
        """Extract skills from experience-related text."""
        skills = []
        
        # Look for experience with specific technologies or concepts
        exp_patterns = [
            r"experience (?:in|with) ([^,.]+)",
            r"responsible for ([^,.]+)",
            r"managed ([^,.]+)",
            r"developed ([^,.]+)",
            r"implemented ([^,.]+)",
            r"led ([^,.]+)",
            r"created ([^,.]+)",
            r"designed ([^,.]+)",
            r"built ([^,.]+)"
        ]
        
        for pattern in exp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    skills.append(match.group(1).strip())
        
        # Look for specific job titles
        job_titles = [
            "Engineer", "Manager", "Director", "Developer", "Analyst", "Consultant",
            "Technician", "Specialist", "Coordinator", "Administrator"
        ]
        
        for title in job_titles:
            if title.lower() in text.lower():
                skills.append(f"{title} experience")
        
        return skills
    
    def _extract_social_skills(self, text: str) -> List[str]:
        """Extract skills from social media profiles."""
        skills = []
        
        # Look for skills, endorsements, recommendations
        social_patterns = [
            r"skill(?:s|ed)? (?:in|with) ([^,.]+)",
            r"endorsed for ([^,.]+)",
            r"recommended for ([^,.]+)",
            r"expertise (?:in|with) ([^,.]+)"
        ]
        
        for pattern in social_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    skills.append(match.group(1).strip())
        
        return skills
    
    def _extract_general_skills(self, text: str) -> List[str]:
        """Extract general skills from text."""
        skills = []
        
        # Generic patterns for skills
        general_patterns = [
            r"skill(?:s|ed)? (?:in|with) ([^,.]+)",
            r"proficient (?:in|with) ([^,.]+)",
            r"knowledge of ([^,.]+)",
            r"familiar with ([^,.]+)",
            r"expertise (?:in|with) ([^,.]+)",
            r"specialized (?:in|with) ([^,.]+)"
        ]
        
        for pattern in general_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1):
                    skills.append(match.group(1).strip())
        
        return skills
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize and deduplicate skills."""
        normalized = []
        seen = set()
        
        for skill in skills:
            # Convert to lowercase for comparison
            normalized_skill = skill.lower().strip()
            
            # Skip if too short or already seen
            if len(normalized_skill) < 3 or normalized_skill in seen:
                continue
                
            # Skip common words that aren't skills
            if normalized_skill in ["and", "the", "with", "for", "this", "that"]:
                continue
                
            seen.add(normalized_skill)
            # Add original case version to the result
            normalized.append(skill.strip())
        
        return normalized
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills as transferable, technical, or soft.
        
        Args:
            skills: List of skills to categorize
            
        Returns:
            Dict with categorized skills
        """
        categorized = {
            "transferable": [],
            "technical": [],
            "soft": []
        }
        
        # Technical skill keywords
        technical_keywords = [
            "programming", "software", "analytics", "analysis", "engineering", 
            "design", "development", "solar", "wind", "renewable", "energy", 
            "efficiency", "building", "construction", "installation", "manufacturing",
            "maintenance", "repair", "operation", "simulation", "modeling", "coding",
            "python", "java", "javascript", "html", "css", "database", "sql", "nosql",
            "api", "aws", "cloud", "docker", "kubernetes", "devops", "cicd", "git",
            "linux", "windows", "macos", "android", "ios", "mobile", "web", "frontend",
            "backend", "fullstack", "ui", "ux", "testing", "qa", "agile", "scrum",
            "lean", "kanban", "waterfall", "jira", "confluence", "excel", "word",
            "powerpoint", "google", "adobe", "photoshop", "illustrator", "indesign",
            "premiere", "lightroom", "acrobat", "audition", "cad", "autocad", "revit",
            "sketchup", "3d", "modeling", "rendering", "architecture", "planning",
            "gis", "mapping", "data", "machine learning", "artificial intelligence",
            "ai", "ml", "deep learning", "natural language processing", "nlp",
            "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn",
            "pandas", "numpy", "r", "matlab", "tableau", "power bi", "looker",
            "statistics", "calculus", "linear algebra", "discrete math", "algorithms",
            "data structures", "networks", "protocols", "security", "cybersecurity",
            "penetration testing", "ethical hacking", "encryption", "blockchain",
            "cryptocurrency", "bitcoin", "ethereum", "solidity", "smart contracts",
            "hvac", "electrical", "plumbing", "welding", "machining", "cnc", "robotics",
            "automation", "control systems", "instrumentation", "scada", "certification"
        ]
        
        # Soft skill keywords
        soft_keywords = [
            "communication", "teamwork", "leadership", "management", "public speaking",
            "presentation", "interpersonal", "negotiation", "persuasion", "writing",
            "verbal", "listening", "empathy", "emotional intelligence", "eq", "patience",
            "conflict resolution", "problem solving", "critical thinking", "creativity",
            "innovation", "adaptability", "flexibility", "resilience", "time management",
            "organization", "planning", "prioritization", "detail oriented", "multitasking",
            "decision making", "strategic thinking", "analytical thinking", "research",
            "customer service", "client relations", "sales", "marketing", "budgeting",
            "financial planning", "coaching", "mentoring", "teaching", "training",
            "facilitation", "delegation", "motivation", "inspiration", "cultural awareness",
            "diversity", "inclusion", "ethics", "integrity", "responsibility", "accountability",
            "initiative", "self-motivated", "independent", "autonomous", "resourcefulness",
            "persistence", "grit", "determination", "ambition", "goal setting", "networking",
            "relationship building", "collaboration", "cooperation", "diplomacy", "tact"
        ]
        
        # Transferable skill keywords
        transferable_keywords = [
            "project management", "coordination", "supervision", "reporting", "documentation",
            "compliance", "regulation", "quality control", "quality assurance", "inspection",
            "assessment", "evaluation", "monitoring", "measurement", "analysis", "synthesis",
            "research", "investigation", "exploration", "discovery", "process improvement",
            "optimization", "efficiency", "effectiveness", "productivity", "performance",
            "benchmarking", "metrics", "kpis", "scheduling", "logistics", "procurement",
            "purchasing", "vendor management", "supplier relations", "contract management",
            "negotiation", "mediation", "conflict resolution", "problem solving", "troubleshooting",
            "debugging", "risk management", "risk assessment", "risk mitigation", "disaster recovery",
            "business continuity", "strategic planning", "tactical planning", "operational planning",
            "budgeting", "forecasting", "financial analysis", "cost reduction", "revenue generation",
            "profit maximization", "sales", "marketing", "customer service", "client relations",
            "stakeholder management", "team building", "team leadership", "coaching", "mentoring",
            "training", "development", "onboarding", "talent acquisition", "recruitment",
            "interviewing", "selection", "retention", "performance review", "feedback",
            "communication", "presentation", "public speaking", "writing", "editing",
            "proofreading", "translation", "interpretation", "facilitation", "moderation"
        ]
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check if skill contains any technical keywords
            is_technical = any(keyword in skill_lower for keyword in technical_keywords)
            
            # Check if skill contains any soft keywords
            is_soft = any(keyword in skill_lower for keyword in soft_keywords)
            
            # Check if skill contains any transferable keywords
            is_transferable = any(keyword in skill_lower for keyword in transferable_keywords)
            
            # Add to appropriate categories
            if is_technical:
                categorized["technical"].append(skill)
            if is_soft:
                categorized["soft"].append(skill)
            if is_transferable or (not is_technical and not is_soft):
                # If not clearly technical or soft, consider it transferable
                categorized["transferable"].append(skill)
                
        # Deduplicate each category
        for category in categorized:
            categorized[category] = list(set(categorized[category]))
            
        return categorized
    
    def verify_enrichment_data(self, user_profile: Dict[str, Any], verified_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile with verified enrichment data.
        
        Args:
            user_profile: User profile to update
            verified_data: Verified enrichment data
            
        Returns:
            Updated user profile
        """
        # Create a copy of the profile to avoid modifying the original
        updated_profile = user_profile.copy()
        
        # Update the enrichment data with verified data
        if "enrichment" in updated_profile:
            # Update skills
            if "skills" in verified_data:
                updated_profile["enrichment"]["skills"] = verified_data["skills"]
            
            # Mark as verified
            updated_profile["enrichment"]["verified"] = True
            updated_profile["enrichment"]["needs_verification"] = False
            updated_profile["enrichment"]["last_updated"] = self._get_current_timestamp()
            
            logger.info(f"Enrichment data verified for user: {updated_profile.get('name', 'Unknown')}")
        else:
            logger.warning(f"Cannot verify enrichment data: No enrichment data found in profile")
        
        return updated_profile
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Singleton instance for easy access
enricher = ProfileEnricher()

async def enrich_user_profile(user_profile: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Enrich user profile with additional information.
    
    Args:
        user_profile: User profile to enrich
        **kwargs: Additional arguments for ProfileEnricher.enrich_user_profile
        
    Returns:
        Enriched user profile
    """
    return await enricher.enrich_user_profile(user_profile, **kwargs)

async def verify_enrichment_data(user_profile: Dict[str, Any], verified_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user profile with verified enrichment data.
    
    Args:
        user_profile: User profile to update
        verified_data: Verified enrichment data
        
    Returns:
        Updated user profile
    """
    return enricher.verify_enrichment_data(user_profile, verified_data)

if __name__ == "__main__":
    import sys
    import json
    
    async def main():
        # Get user profile from command line
        if len(sys.argv) < 2:
            print("Please provide user profile JSON", file=sys.stderr)
            sys.exit(1)
        
        try:
            # Parse user profile
            user_profile = json.loads(sys.argv[1])
            
            # Enrich profile
            enriched_profile = await enrich_user_profile(user_profile)
            
            # Print enriched profile as JSON
            print(json.dumps(enriched_profile, indent=2))
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    # Run main function
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main()) 