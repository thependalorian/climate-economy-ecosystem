#!/usr/bin/env python3
"""
Gateway City Analyzer for Massachusetts Clean Energy Ecosystem

This tool analyzes opportunities, programs, and resources specific to 
Massachusetts Gateway Cities for the clean energy sector.

Usage:
    python gateway_city_analyzer.py "Lawrence" "solar installation"
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

# Massachusetts Gateway Cities
# Source: Massachusetts Executive Office of Housing and Economic Development
GATEWAY_CITIES = [
    {"name": "Attleboro", "lat": 41.9445, "lng": -71.2856},
    {"name": "Barnstable", "lat": 41.7003, "lng": -70.3000},
    {"name": "Brockton", "lat": 42.0834, "lng": -71.0183},
    {"name": "Chelsea", "lat": 42.3917, "lng": -71.0328},
    {"name": "Chicopee", "lat": 42.1487, "lng": -72.6078},
    {"name": "Everett", "lat": 42.4084, "lng": -71.0537},
    {"name": "Fall River", "lat": 41.7014, "lng": -71.1550},
    {"name": "Fitchburg", "lat": 42.5834, "lng": -71.8028},
    {"name": "Haverhill", "lat": 42.7762, "lng": -71.0773},
    {"name": "Holyoke", "lat": 42.2042, "lng": -72.6162},
    {"name": "Lawrence", "lat": 42.7070, "lng": -71.1631},
    {"name": "Leominster", "lat": 42.5251, "lng": -71.7598},
    {"name": "Lowell", "lat": 42.6334, "lng": -71.3162},
    {"name": "Lynn", "lat": 42.4668, "lng": -70.9495},
    {"name": "Malden", "lat": 42.4251, "lng": -71.0662},
    {"name": "Methuen", "lat": 42.7262, "lng": -71.1908},
    {"name": "New Bedford", "lat": 41.6362, "lng": -70.9342},
    {"name": "Peabody", "lat": 42.5278, "lng": -70.9286},
    {"name": "Pittsfield", "lat": 42.4500, "lng": -73.2597},
    {"name": "Quincy", "lat": 42.2529, "lng": -71.0023},
    {"name": "Revere", "lat": 42.4084, "lng": -71.0120},
    {"name": "Salem", "lat": 42.5195, "lng": -70.8967},
    {"name": "Springfield", "lat": 42.1015, "lng": -72.5898},
    {"name": "Taunton", "lat": 41.9000, "lng": -71.0900},
    {"name": "Westfield", "lat": 42.1250, "lng": -72.7496},
    {"name": "Worcester", "lat": 42.2626, "lng": -71.8023}
]

# Gateway City characteristics and focus areas
GATEWAY_CITY_SPECIALIZATIONS = {
    "Attleboro": ["Manufacturing", "Solar", "Energy Efficiency"],
    "Barnstable": ["Offshore Wind", "Coastal Resilience", "Tourism"],
    "Brockton": ["Energy Efficiency", "Workforce Development", "Building Retrofits"],
    "Chelsea": ["Climate Resilience", "Environmental Justice", "Urban Sustainability"],
    "Chicopee": ["Manufacturing", "Energy Efficiency", "Solar"],
    "Everett": ["Clean Transportation", "Climate Resilience", "Urban Sustainability"],
    "Fall River": ["Offshore Wind", "Manufacturing", "Coastal Resilience"],
    "Fitchburg": ["Energy Efficiency", "Renewable Energy", "Building Retrofits"],
    "Haverhill": ["Energy Efficiency", "Building Retrofits", "Clean Transportation"],
    "Holyoke": ["Solar", "Hydropower", "Smart Grid"],
    "Lawrence": ["Energy Efficiency", "Workforce Development", "Solar"],
    "Leominster": ["Manufacturing", "Energy Efficiency", "Renewable Energy"],
    "Lowell": ["Clean Transportation", "Solar", "Green Innovation"],
    "Lynn": ["Coastal Resilience", "Energy Efficiency", "Offshore Wind"],
    "Malden": ["Energy Efficiency", "Climate Resilience", "Urban Sustainability"],
    "Methuen": ["Energy Efficiency", "Building Retrofits", "Renewable Energy"],
    "New Bedford": ["Offshore Wind", "Port Development", "Coastal Resilience"],
    "Peabody": ["Energy Efficiency", "Renewable Energy", "Urban Sustainability"],
    "Pittsfield": ["Energy Efficiency", "Rural Clean Energy", "Building Retrofits"],
    "Quincy": ["Coastal Resilience", "Energy Efficiency", "Clean Transportation"],
    "Revere": ["Coastal Resilience", "Climate Adaptation", "Energy Efficiency"],
    "Salem": ["Offshore Wind", "Coastal Resilience", "Clean Transportation"],
    "Springfield": ["Energy Efficiency", "Building Retrofits", "Clean Transportation"],
    "Taunton": ["Manufacturing", "Energy Efficiency", "Renewable Energy"],
    "Westfield": ["Energy Efficiency", "Rural Clean Energy", "Building Retrofits"],
    "Worcester": ["Energy Efficiency", "Green Innovation", "Building Retrofits"]
}

# Key clean energy initiatives by Gateway City
GATEWAY_CITY_INITIATIVES = {
    "Attleboro": [
        "Renewable Energy Trust Fund projects",
        "Municipal building energy efficiency upgrades",
        "Solar installations on municipal properties"
    ],
    "Barnstable": [
        "Vineyard Wind connection point",
        "Cape Light Compact energy efficiency programs",
        "Coastal resilience planning"
    ],
    "Brockton": [
        "Brightfields solar project on former brownfield",
        "Green workforce training programs",
        "Municipal building energy efficiency upgrades"
    ],
    "Chelsea": [
        "Climate resilience planning with GreenRoots",
        "Environmental justice advocacy",
        "Municipal vulnerability preparedness program"
    ],
    "Holyoke": [
        "Mt. Tom Solar Farm (former coal plant site)",
        "Holyoke Gas & Electric renewable portfolio",
        "Smart grid innovations through HG&E"
    ],
    "Lawrence": [
        "Groundwork Lawrence green initiatives",
        "Lawrence Partnership workforce development",
        "Community clean energy projects"
    ],
    "Lowell": [
        "UMass Lowell clean energy research",
        "Lowell Green Building Commission",
        "Canal system hydropower modernization"
    ],
    "New Bedford": [
        "New Bedford Marine Commerce Terminal (offshore wind)",
        "Community Preservation Act efficiency projects",
        "Port electrification planning"
    ],
    "Pittsfield": [
        "Energy efficiency retrofits for municipal buildings",
        "Berkshire Innovation Center clean tech support",
        "Rural clean energy demonstration projects"
    ],
    "Worcester": [
        "Green Worcester Plan implementation",
        "Clark University Climate Action Plan",
        "Worcester Regional Food Hub energy efficiency"
    ]
}

# Training programs specific to Gateway Cities
GATEWAY_CITY_TRAINING = {
    "Lawrence": [
        {"name": "MassHire Merrimack Valley Career Center", "focus": "Green Jobs Training", "url": "https://masshiremvcc.com/"},
        {"name": "Northern Essex Community College", "focus": "Clean Energy Certificate Programs", "url": "https://www.necc.mass.edu/"}
    ],
    "Worcester": [
        {"name": "Worcester CleanTech Incubator", "focus": "Clean Energy Entrepreneurship", "url": "https://www.wcti.org/"},
        {"name": "Quinsigamond Community College", "focus": "Energy Utility Technology", "url": "https://www.qcc.edu/"}
    ],
    "New Bedford": [
        {"name": "Bristol Community College", "focus": "Offshore Wind Power Technology", "url": "https://www.bristolcc.edu/"},
        {"name": "New Bedford Wind Energy Center", "focus": "Offshore Wind Technical Training", "url": "https://newbedfordwec.org/"}
    ],
    "Springfield": [
        {"name": "Springfield Technical Community College", "focus": "Energy Systems Technology", "url": "https://www.stcc.edu/"},
        {"name": "MassHire Springfield Career Center", "focus": "Green Construction Training", "url": "https://masshirespringfield.org/"}
    ],
    "Lowell": [
        {"name": "Middlesex Community College", "focus": "Sustainable Energy Programs", "url": "https://www.middlesex.mass.edu/"},
        {"name": "UMass Lowell Continuing Education", "focus": "Clean Energy Engineering", "url": "https://www.uml.edu/"}
    ]
}

def is_gateway_city(city_name: str) -> bool:
    """
    Check if a city is a Massachusetts Gateway City.
    
    Args:
        city_name: Name of the city to check
        
    Returns:
        Boolean indicating if it's a Gateway City
    """
    normalized_name = city_name.strip().lower()
    return any(city["name"].lower() == normalized_name for city in GATEWAY_CITIES)

def find_nearest_gateway_cities(lat: float, lng: float, max_distance_km: float = 30) -> List[Dict[str, Any]]:
    """
    Find Gateway Cities within a specified distance of a location.
    
    Args:
        lat: Latitude of the location
        lng: Longitude of the location
        max_distance_km: Maximum distance in kilometers
        
    Returns:
        List of nearby Gateway Cities with distances
    """
    nearby_cities = []
    
    for city in GATEWAY_CITIES:
        distance = calculate_distance(lat, lng, city["lat"], city["lng"])
        if distance <= max_distance_km:
            nearby_cities.append({
                "name": city["name"],
                "distance_km": round(distance, 1),
                "lat": city["lat"],
                "lng": city["lng"]
            })
    
    # Sort by distance
    return sorted(nearby_cities, key=lambda x: x["distance_km"])

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

def get_gateway_city_info(city_name: str) -> Dict[str, Any]:
    """
    Get comprehensive information about a Gateway City.
    
    Args:
        city_name: Name of the Gateway City
        
    Returns:
        Dict with city information
    """
    normalized_name = city_name.strip()
    
    # Find the city in our list
    city_data = next((city for city in GATEWAY_CITIES if city["name"] == normalized_name), None)
    if not city_data:
        return {"error": f"{normalized_name} is not a recognized Massachusetts Gateway City"}
    
    # Get specializations and initiatives
    specializations = GATEWAY_CITY_SPECIALIZATIONS.get(normalized_name, [])
    initiatives = GATEWAY_CITY_INITIATIVES.get(normalized_name, [])
    training_programs = GATEWAY_CITY_TRAINING.get(normalized_name, [])
    
    # Get additional data from database if available
    additional_data = get_city_data_from_db(normalized_name)
    
    # Combine all information
    return {
        "name": normalized_name,
        "coordinates": {"lat": city_data["lat"], "lng": city_data["lng"]},
        "is_gateway_city": True,
        "clean_energy_specializations": specializations,
        "key_initiatives": initiatives,
        "training_programs": training_programs,
        "additional_resources": additional_data
    }

def get_city_data_from_db(city_name: str) -> Dict[str, Any]:
    """
    Get additional city data from the database.
    
    Args:
        city_name: Name of the city
        
    Returns:
        Dict with additional city data
    """
    try:
        # Query for training programs
        training_query = supabase.table("training_programs") \
            .select("*") \
            .ilike("location", f"%{city_name}%") \
            .execute()
            
        training_programs = training_query.data if hasattr(training_query, 'data') else []
        
        # Query for job opportunities
        jobs_query = supabase.table("job_opportunities") \
            .select("*") \
            .ilike("location", f"%{city_name}%") \
            .execute()
            
        job_opportunities = jobs_query.data if hasattr(jobs_query, 'data') else []
        
        # Get EJ communities within the city
        ej_communities = []  # This would come from a separate EJ communities database or API
        
        return {
            "training_programs": training_programs,
            "job_opportunities": job_opportunities,
            "ej_communities": ej_communities
        }
        
    except Exception as e:
        logger.error(f"Error fetching city data from database: {str(e)}")
        return {}

def analyze_opportunities(city_name: str, sector: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze clean energy opportunities in a Gateway City.
    
    Args:
        city_name: Name of the Gateway City
        sector: Optional clean energy sector to focus on
        
    Returns:
        Dict with opportunity analysis
    """
    # Verify it's a Gateway City
    if not is_gateway_city(city_name):
        return {
            "error": f"{city_name} is not a recognized Massachusetts Gateway City",
            "suggested_gateway_cities": [city["name"] for city in GATEWAY_CITIES[:5]]
        }
    
    # Get city information
    city_info = get_gateway_city_info(city_name)
    
    # Filter specializations by sector if provided
    if sector and sector.strip():
        relevant_specializations = [
            spec for spec in city_info["clean_energy_specializations"]
            if sector.lower() in spec.lower()
        ]
    else:
        relevant_specializations = city_info["clean_energy_specializations"]
    
    # Get AI-enhanced insights
    insights = generate_opportunity_insights(city_name, sector, city_info)
    
    # Construct the full analysis
    analysis = {
        "city": city_info["name"],
        "is_gateway_city": True,
        "relevant_specializations": relevant_specializations,
        "key_initiatives": city_info["key_initiatives"],
        "training_programs": city_info["training_programs"],
        "job_opportunities": city_info.get("additional_resources", {}).get("job_opportunities", []),
        "workforce_insights": insights["workforce_insights"],
        "opportunity_areas": insights["opportunity_areas"],
        "funding_sources": insights["funding_sources"]
    }
    
    return analysis

def generate_opportunity_insights(city_name: str, sector: Optional[str], city_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-enhanced insights about opportunities in a Gateway City.
    
    Args:
        city_name: Name of the Gateway City
        sector: Optional clean energy sector to focus on
        city_info: City information data
        
    Returns:
        Dict with AI-generated insights
    """
    try:
        # Create prompt for OpenAI
        sector_text = f"in the {sector} sector" if sector else "across clean energy sectors"
        
        specializations = ", ".join(city_info["clean_energy_specializations"])
        initiatives = ", ".join(city_info["key_initiatives"][:3]) if city_info["key_initiatives"] else "No major initiatives listed"
        
        prompt = f"""
        Analyze workforce and economic opportunities {sector_text} for {city_name}, Massachusetts, a Gateway City.
        
        City specializations: {specializations}
        Key initiatives: {initiatives}
        
        Provide insights in JSON format with these fields:
        1. "workforce_insights": List of 3-5 specific workforce development insights for this city
        2. "opportunity_areas": List of 3-5 specific clean energy economic opportunities
        3. "funding_sources": List of 3-5 potential funding sources or programs applicable to this city
        
        Focus on Massachusetts-specific programs, funding sources, and practical opportunities based on the city's profile.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in Massachusetts clean energy economic development with special focus on Gateway Cities. Provide practical, specific insights based on current Massachusetts programs and initiatives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse response
        response_text = response.choices[0].message.content
        insights = json.loads(response_text)
        
        return {
            "workforce_insights": insights.get("workforce_insights", []),
            "opportunity_areas": insights.get("opportunity_areas", []),
            "funding_sources": insights.get("funding_sources", [])
        }
            
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return {
            "workforce_insights": [
                "Workforce data temporarily unavailable - please try again later"
            ],
            "opportunity_areas": [
                "Based on Gateway City status, likely opportunities in energy efficiency and building retrofits",
                "Clean energy manufacturing may align with traditional manufacturing base",
                "Training partnerships with community colleges offer potential"
            ],
            "funding_sources": [
                "MassCEC workforce development grants",
                "Massachusetts Clean Energy Center funding programs",
                "Mass Save incentive programs for energy efficiency"
            ]
        }

def find_training_programs(city_name: str, sector: Optional[str] = None, distance_km: int = 30) -> List[Dict[str, Any]]:
    """
    Find training programs in or near a Gateway City.
    
    Args:
        city_name: Name of the city
        sector: Optional clean energy sector to filter by
        distance_km: Maximum distance in kilometers
        
    Returns:
        List of relevant training programs
    """
    # Get city coordinates
    city_data = next((city for city in GATEWAY_CITIES if city["name"] == city_name), None)
    if not city_data:
        return []
    
    lat, lng = city_data["lat"], city_data["lng"]
    
    # Look for nearby Gateway Cities if no direct programs available
    nearby_cities = find_nearest_gateway_cities(lat, lng, distance_km)
    
    # Collect programs from city and nearby cities
    all_programs = []
    
    # Add programs from the target city
    city_programs = GATEWAY_CITY_TRAINING.get(city_name, [])
    for program in city_programs:
        program["city"] = city_name
        program["distance_km"] = 0
        all_programs.append(program)
    
    # Add programs from nearby cities
    for nearby in nearby_cities:
        if nearby["name"] != city_name:  # Skip the target city, already processed
            nearby_programs = GATEWAY_CITY_TRAINING.get(nearby["name"], [])
            for program in nearby_programs:
                program["city"] = nearby["name"]
                program["distance_km"] = nearby["distance_km"]
                all_programs.append(program)
    
    # Filter by sector if specified
    if sector:
        sector_lower = sector.lower()
        filtered_programs = [
            program for program in all_programs
            if sector_lower in program["focus"].lower()
        ]
        return filtered_programs if filtered_programs else all_programs  # Fall back to all if none match
    
    # Sort by distance
    return sorted(all_programs, key=lambda x: x["distance_km"])

def main(city_name: str, sector: Optional[str] = None):
    """
    Main function to analyze a Gateway City.
    
    Args:
        city_name: Name of the Gateway City to analyze
        sector: Optional clean energy sector to focus on
    """
    if not city_name:
        print("Please provide a city name")
        return
    
    # Analyze opportunities
    results = analyze_opportunities(city_name, sector)
    
    # Print results
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else None
    sector = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(city, sector)
