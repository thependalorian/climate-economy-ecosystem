#!/usr/bin/env python3
"""
Environmental Justice Support Tool for Massachusetts Clean Energy Ecosystem

This tool identifies Environmental Justice (EJ) communities in Massachusetts 
and provides specialized support and resources for clean energy opportunities.

Usage:
    python ej_support.py "Chelsea" "clean energy jobs"
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from math import radians, cos, sin, asin, sqrt
import re

import openai
from openai import OpenAI
from dotenv import load_dotenv
import requests
from supabase import create_client, Client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Massachusetts EJ Communities
# Source: MassGIS Environmental Justice Populations
# These are examples - a real implementation would use a complete database or API
EJ_COMMUNITIES = [
    {
        "name": "Chelsea",
        "lat": 42.3917,
        "lng": -71.0328,
        "criteria": ["income", "minority", "english isolation"],
        "census_tracts": ["25025050100", "25025050200", "25025050300"],
        "gateway_city": True
    },
    {
        "name": "Lawrence",
        "lat": 42.7070,
        "lng": -71.1631,
        "criteria": ["income", "minority", "english isolation"],
        "census_tracts": ["2502535300", "2502535400", "2502535500"],
        "gateway_city": True
    },
    {
        "name": "Springfield - Metro Center",
        "lat": 42.1015,
        "lng": -72.5898,
        "criteria": ["income", "minority"],
        "census_tracts": ["2501382500", "2501382600"],
        "gateway_city": True
    },
    {
        "name": "Dorchester",
        "lat": 42.3016,
        "lng": -71.0676,
        "criteria": ["income", "minority", "english isolation"],
        "census_tracts": ["25025090600", "25025090700", "25025090800"],
        "gateway_city": False
    },
    {
        "name": "New Bedford - South Central",
        "lat": 41.6362,
        "lng": -70.9342,
        "criteria": ["income", "minority"],
        "census_tracts": ["2500565500", "2500565600"],
        "gateway_city": True
    },
    {
        "name": "Holyoke",
        "lat": 42.2042,
        "lng": -72.6162,
        "criteria": ["income", "minority", "english isolation"],
        "census_tracts": ["2501380400", "2501380500"],
        "gateway_city": True
    },
    {
        "name": "Lynn",
        "lat": 42.4668,
        "lng": -70.9495,
        "criteria": ["income", "minority", "english isolation"],
        "census_tracts": ["2500930700", "2500930800"],
        "gateway_city": True
    },
    {
        "name": "Lowell",
        "lat": 42.6334,
        "lng": -71.3162,
        "criteria": ["income", "minority", "english isolation"],
        "census_tracts": ["2501731100", "2501731200"],
        "gateway_city": True
    },
    {
        "name": "Worcester - Main South",
        "lat": 42.2526,
        "lng": -71.8023,
        "criteria": ["income", "minority"],
        "census_tracts": ["2502700900", "2502701000"],
        "gateway_city": True
    },
    {
        "name": "Brockton",
        "lat": 42.0834,
        "lng": -71.0183,
        "criteria": ["income", "minority"],
        "census_tracts": ["2502390100", "2502390200"],
        "gateway_city": True
    }
]

# EJ-specific support programs
EJ_SUPPORT_PROGRAMS = [
    {
        "name": "MassCEC Equity Workforce Training Grants",
        "description": "Funding for clean energy job training programs serving Environmental Justice populations",
        "funding_range": "$50,000 - $500,000",
        "url": "https://www.masscec.com/program/equity-workforce-training",
        "eligibility": ["EJ communities", "minority-owned businesses", "women-owned businesses"],
        "sectors": ["All clean energy sectors"]
    },
    {
        "name": "Green Jobs Academy",
        "description": "Focused training for residents of EJ communities for careers in energy efficiency, solar, and clean transportation",
        "funding_range": "Free training for eligible participants",
        "url": "https://masscec.com/green-jobs-academy",
        "eligibility": ["EJ community residents", "low-income individuals"],
        "sectors": ["Energy efficiency", "Solar", "Clean transportation"]
    },
    {
        "name": "Community Action Weatherization Programs",
        "description": "Home weatherization services for income-eligible residents, with employment opportunities",
        "funding_range": "Varies by region",
        "url": "https://www.mass.gov/service-details/weatherization-assistance-program-wap",
        "eligibility": ["Income-eligible households", "EJ community residents"],
        "sectors": ["Energy efficiency", "Building retrofits"]
    },
    {
        "name": "Clean Energy Entrepreneurship Accelerator",
        "description": "Business development support for entrepreneurs from underrepresented groups",
        "funding_range": "$10,000 - $50,000 plus mentorship",
        "url": "https://masscec.com/entrepreneur-support",
        "eligibility": ["Minority entrepreneurs", "Women entrepreneurs", "EJ community businesses"],
        "sectors": ["All clean energy sectors"]
    },
    {
        "name": "Mass Solar Loan Program",
        "description": "Low-interest loans for solar PV systems with additional incentives for income-eligible residents",
        "funding_range": "Income-based incentives up to 30% of project cost",
        "url": "https://www.masssolarloan.com/",
        "eligibility": ["Income-eligible households", "EJ community residents"],
        "sectors": ["Solar"]
    }
]

# EJ-specific clean energy initiatives
EJ_INITIATIVES = [
    {
        "name": "Environmental Justice Task Force",
        "organization": "Massachusetts Clean Energy Center",
        "description": "Focusing resources and opportunities in EJ communities",
        "url": "https://www.masscec.com/environmental-justice"
    },
    {
        "name": "Solar Access Program",
        "organization": "Massachusetts Department of Energy Resources",
        "description": "Increasing solar adoption in low-income neighborhoods",
        "url": "https://www.mass.gov/solar-access-program"
    },
    {
        "name": "Clean Energy & Climate Plan for 2025/2030 EJ Provisions",
        "organization": "Executive Office of Energy & Environmental Affairs",
        "description": "Dedicated policies ensuring benefits of clean energy reach EJ communities",
        "url": "https://www.mass.gov/doc/clean-energy-and-climate-plan-for-2025-and-2030/download"
    },
    {
        "name": "Community-First Solar",
        "organization": "Multiple partners",
        "description": "Prioritizing solar development that benefits local communities",
        "url": "https://www.masscec.com/community-first-solar"
    },
    {
        "name": "Transportation Justice",
        "organization": "Massachusetts Department of Transportation",
        "description": "Electrification of public transit routes serving EJ communities",
        "url": "https://www.mass.gov/info-details/environmental-justice-at-massdot"
    }
]

# EJ community training providers
EJ_TRAINING_PROVIDERS = [
    {
        "name": "Building Pathways",
        "location": "Boston",
        "description": "Pre-apprenticeship program focused on building trades including clean energy",
        "url": "https://buildingpathwaysboston.org/",
        "serves_ej": True,
        "program_length": "7 weeks",
        "eligibility": "Priority for Boston residents, women, people of color"
    },
    {
        "name": "IBEW Local 103 Electrical Workers Minority Caucus",
        "location": "Dorchester",
        "description": "Electrical apprenticeship pathway with outreach to minority communities",
        "url": "https://www.ibew103.com/",
        "serves_ej": True,
        "program_length": "5-year apprenticeship",
        "eligibility": "Open to all, with targeted recruiting in EJ communities"
    },
    {
        "name": "Chelsea GreenRoots",
        "location": "Chelsea",
        "description": "Community-based environmental justice organization with green jobs component",
        "url": "https://www.greenrootschelsea.org/",
        "serves_ej": True,
        "program_length": "Varies by program",
        "eligibility": "Chelsea residents, with focus on Spanish speakers"
    },
    {
        "name": "Worcester Youth Center Green Jobs Training",
        "location": "Worcester",
        "description": "Youth-focused training for green careers",
        "url": "https://worcesteryouthcenter.org/",
        "serves_ej": True,
        "program_length": "12 weeks",
        "eligibility": "Worcester youth ages 16-24"
    },
    {
        "name": "Roxbury Community College Green Energy Program",
        "location": "Roxbury",
        "description": "Certificate and degree programs in renewable energy and energy efficiency",
        "url": "https://www.rcc.mass.edu/",
        "serves_ej": True,
        "program_length": "1-2 years",
        "eligibility": "Open enrollment, financial aid available"
    }
]

def is_ej_community(location: str) -> bool:
    """
    Check if a location is recognized as an Environmental Justice community.
    
    Args:
        location: Name of the location to check
        
    Returns:
        Boolean indicating if it's an EJ community
    """
    normalized_name = location.strip().lower()
    
    # Check for exact matches first
    if any(community["name"].lower() == normalized_name for community in EJ_COMMUNITIES):
        return True
        
    # Check for partial matches (e.g., "Chelsea, MA" should match "Chelsea")
    return any(community["name"].lower() in normalized_name for community in EJ_COMMUNITIES)

def get_ej_criteria(location: str) -> List[str]:
    """
    Get the EJ criteria that apply to a community.
    
    Args:
        location: Name of the EJ community
        
    Returns:
        List of applicable EJ criteria
    """
    normalized_name = location.strip().lower()
    
    for community in EJ_COMMUNITIES:
        if community["name"].lower() == normalized_name or community["name"].lower() in normalized_name:
            return community["criteria"]
            
    return []

def find_nearest_ej_communities(lat: float, lng: float, max_distance_km: float = 10) -> List[Dict[str, Any]]:
    """
    Find Environmental Justice communities within a specified distance.
    
    Args:
        lat: Latitude of the location
        lng: Longitude of the location
        max_distance_km: Maximum distance in kilometers
        
    Returns:
        List of nearby EJ communities with distances
    """
    nearby_communities = []
    
    for community in EJ_COMMUNITIES:
        distance = calculate_distance(lat, lng, community["lat"], community["lng"])
        if distance <= max_distance_km:
            nearby_communities.append({
                "name": community["name"],
                "distance_km": round(distance, 1),
                "criteria": community["criteria"],
                "gateway_city": community.get("gateway_city", False)
            })
    
    # Sort by distance
    return sorted(nearby_communities, key=lambda x: x["distance_km"])

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first location
        lon1: Longitude of first location
        lat2: Latitude of second location
        lon2: Longitude of second location
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    
    return c * r

def get_ej_community_info(location: str) -> Dict[str, Any]:
    """
    Get comprehensive information about an EJ community.
    
    Args:
        location: Name of the EJ community
        
    Returns:
        Dict with community information
    """
    # Normalize location name
    normalized_name = location.strip()
    
    # Find the community
    community_data = None
    for community in EJ_COMMUNITIES:
        if community["name"].lower() == normalized_name.lower() or community["name"].lower() in normalized_name.lower():
            community_data = community
            break
            
    if not community_data:
        return {"error": f"{normalized_name} is not a recognized Environmental Justice community"}
    
    # Get additional data from database if available
    additional_data = get_ej_data_from_db(normalized_name)
    
    # Get support programs
    relevant_programs = find_ej_support_programs(community_data["criteria"])
    
    # Get training providers
    training_providers = find_training_providers_for_ej(normalized_name)
    
    # Combine all information
    return {
        "name": community_data["name"],
        "coordinates": {"lat": community_data["lat"], "lng": community_data["lng"]},
        "is_ej_community": True,
        "ej_criteria": community_data["criteria"],
        "is_gateway_city": community_data.get("gateway_city", False),
        "census_tracts": community_data.get("census_tracts", []),
        "support_programs": relevant_programs,
        "training_providers": training_providers,
        "additional_resources": additional_data
    }

def get_ej_data_from_db(location: str) -> Dict[str, Any]:
    """
    Get additional EJ community data from the database.
    
    Args:
        location: Name of the EJ community
        
    Returns:
        Dict with additional community data
    """
    try:
        # Query for training programs with EJ focus
        training_query = supabase.table("training_programs") \
            .select("*") \
            .eq("is_ej_focused", True) \
            .ilike("location", f"%{location}%") \
            .execute()
            
        ej_training_programs = training_query.data if hasattr(training_query, 'data') else []
        
        # Query for job opportunities with EJ focus
        jobs_query = supabase.table("job_opportunities") \
            .select("*") \
            .eq("is_ej_friendly", True) \
            .ilike("location", f"%{location}%") \
            .execute()
            
        ej_job_opportunities = jobs_query.data if hasattr(jobs_query, 'data') else []
        
        return {
            "ej_training_programs": ej_training_programs,
            "ej_job_opportunities": ej_job_opportunities
        }
        
    except Exception as e:
        logger.error(f"Error fetching EJ data from database: {str(e)}")
        return {}

def find_ej_support_programs(criteria: List[str]) -> List[Dict[str, Any]]:
    """
    Find support programs relevant to an EJ community based on its criteria.
    
    Args:
        criteria: List of EJ criteria that apply to the community
        
    Returns:
        List of relevant support programs
    """
    # All programs are returned for now, but in a more sophisticated implementation
    # we could filter programs based on criteria
    return EJ_SUPPORT_PROGRAMS

def find_training_providers_for_ej(location: str, max_distance_km: int = 20) -> List[Dict[str, Any]]:
    """
    Find training providers that serve EJ communities near a location.
    
    Args:
        location: Name of the location
        max_distance_km: Maximum distance in kilometers
        
    Returns:
        List of relevant training providers
    """
    # Find providers that specifically mention the location
    local_providers = [
        provider for provider in EJ_TRAINING_PROVIDERS
        if location.lower() in provider["location"].lower()
    ]
    
    # If we have local providers, return those first
    if local_providers:
        return local_providers
        
    # Otherwise, return all providers that serve EJ communities
    # In a real implementation, we would filter by distance
    return [provider for provider in EJ_TRAINING_PROVIDERS if provider["serves_ej"]]

def analyze_ej_opportunities(location: str, sector: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze clean energy opportunities for an EJ community.
    
    Args:
        location: Name of the EJ community
        sector: Optional clean energy sector to focus on
        
    Returns:
        Dict with opportunity analysis
    """
    # Verify it's an EJ community
    if not is_ej_community(location):
        return {
            "error": f"{location} is not a recognized Environmental Justice community",
            "nearest_ej_communities": [
                community["name"] for community in find_nearest_ej_communities(42.3601, -71.0589, 20)[:5]  # Using Boston as default coordinates
            ]
        }
    
    # Get community information
    community_info = get_ej_community_info(location)
    
    # Get AI-enhanced insights
    insights = generate_ej_insights(location, sector, community_info)
    
    # Construct the full analysis
    analysis = {
        "location": community_info["name"],
        "is_ej_community": True,
        "ej_criteria": community_info["ej_criteria"],
        "is_gateway_city": community_info["is_gateway_city"],
        "support_programs": community_info["support_programs"],
        "training_providers": community_info["training_providers"],
        "job_opportunities": community_info.get("additional_resources", {}).get("ej_job_opportunities", []),
        "ej_specific_insights": insights["ej_specific_insights"],
        "opportunity_areas": insights["opportunity_areas"],
        "barrier_solutions": insights["barrier_solutions"],
        "initiatives": EJ_INITIATIVES
    }
    
    return analysis

def generate_ej_insights(location: str, sector: Optional[str], community_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-enhanced insights about opportunities for an EJ community.
    
    Args:
        location: Name of the EJ community
        sector: Optional clean energy sector to focus on
        community_info: Community information data
        
    Returns:
        Dict with AI-generated insights
    """
    try:
        # Create prompt for OpenAI
        sector_text = f"in the {sector} sector" if sector else "across clean energy sectors"
        
        criteria = ", ".join(community_info["ej_criteria"])
        is_gateway = "Yes" if community_info.get("is_gateway_city") else "No"
        
        prompt = f"""
        Analyze clean energy workforce opportunities {sector_text} for {location}, Massachusetts, an Environmental Justice community.
        
        EJ criteria: {criteria}
        Gateway City: {is_gateway}
        
        Provide insights in JSON format with these fields:
        1. "ej_specific_insights": List of 3-5 insights specifically related to environmental justice considerations
        2. "opportunity_areas": List of 3-5 specific clean energy economic opportunities aligned with EJ priorities
        3. "barrier_solutions": List of 3-5 concrete solutions to overcome barriers facing EJ community residents
        
        Focus on Massachusetts-specific programs, community-based approaches, and practical opportunities based on the community's profile.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in environmental justice and clean energy workforce development in Massachusetts. Provide practical, specific insights based on Massachusetts programs and EJ priorities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse response
        response_text = response.choices[0].message.content
        insights = json.loads(response_text)
        
        return {
            "ej_specific_insights": insights.get("ej_specific_insights", []),
            "opportunity_areas": insights.get("opportunity_areas", []),
            "barrier_solutions": insights.get("barrier_solutions", [])
        }
            
    except Exception as e:
        logger.error(f"Error generating EJ insights: {str(e)}")
        return {
            "ej_specific_insights": [
                "Environmental Justice communities face disproportionate energy burdens",
                "Language barriers may limit access to clean energy opportunities",
                "Transportation access can be a significant barrier to clean energy jobs"
            ],
            "opportunity_areas": [
                "Community solar projects with local hiring requirements",
                "Building weatherization and energy efficiency retrofits",
                "Clean energy job training with wrap-around support services"
            ],
            "barrier_solutions": [
                "Multilingual outreach and application materials",
                "Transportation stipends for training participants",
                "Childcare support during training hours",
                "Pathway programs with local employers"
            ]
        }

def get_ej_support_services(location: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get comprehensive support services for an EJ community.
    
    Args:
        location: Name of the EJ community
        
    Returns:
        Dict with support services by category
    """
    # In a full implementation, this would query a database of support services
    # For now, we return a hardcoded set of services
    
    return {
        "transportation": [
            {
                "name": "Workforce Transportation Program",
                "provider": "MassDOT",
                "description": "Transportation subsidies for workforce training participants",
                "eligibility": "Income-eligible residents of EJ communities",
                "url": "https://www.mass.gov/massdot-workforce-transportation-program"
            }
        ],
        "childcare": [
            {
                "name": "Child Care Access Means Parents in School",
                "provider": "Various community colleges",
                "description": "Childcare subsidies for students in eligible training programs",
                "eligibility": "Income-eligible parents enrolled in qualifying programs",
                "url": "https://www.mass.edu/campuses/childcare.asp"
            }
        ],
        "housing": [
            {
                "name": "Residential Assistance for Families in Transition",
                "provider": "DHCD",
                "description": "Financial assistance to maintain stable housing during training",
                "eligibility": "Income-eligible residents",
                "url": "https://www.mass.gov/service-details/residential-assistance-for-families-in-transition-raft"
            }
        ],
        "language": [
            {
                "name": "English for Clean Energy Careers",
                "provider": "Various providers",
                "description": "Contextualized English language training for clean energy careers",
                "eligibility": "Limited English proficient residents",
                "url": "https://www.mass.gov/english-for-clean-energy"
            }
        ]
    }

def main(location: str, sector: Optional[str] = None):
    """
    Main function to analyze opportunities for an EJ community.
    
    Args:
        location: Name of the EJ community to analyze
        sector: Optional clean energy sector to focus on
    """
    if not location:
        print("Please provide a location")
        return
    
    # Analyze opportunities
    results = analyze_ej_opportunities(location, sector)
    
    # Print results
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    location = sys.argv[1] if len(sys.argv) > 1 else None
    sector = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(location, sector)
