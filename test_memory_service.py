#!/usr/bin/env python3
"""
Test script for Memory Service in Climate Economy Ecosystem

This script tests the Memory Service by:
1. Creating and retrieving memories
2. Storing and retrieving user profiles
3. Testing EJ community detection
4. Simulating resume analysis
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import Memory Service components
from lib.memory.memory_service import MemoryService, ClimateMemoryEntry, UserProfile, MemoryServiceError
print("Using consolidated memory service")

async def test_memory_operations():
    """Test basic memory operations"""
    print("\n=== Testing Memory Operations ===")

    # Initialize memory service
    memory_service = MemoryService()

    # Create a test memory
    test_memory = ClimateMemoryEntry(
        content="Solar installation jobs are growing rapidly in Massachusetts, with a 20% increase in the past year.",
        user_id="test_user",
        category="job_market",
        source="web_search",
        metadata={"url": "https://example.com/solar-jobs-ma", "retrieved_at": datetime.now().isoformat()}
    )

    # Add memory
    memory_id = await memory_service.add_memory(test_memory)
    print(f"Added memory with ID: {memory_id}")

    # Retrieve memory
    retrieved_memory = await memory_service.get_memory_by_id(memory_id)

    # Convert to dict if it's a Pydantic model
    if hasattr(retrieved_memory, "dict") and callable(getattr(retrieved_memory, "dict")):
        retrieved_memory_dict = retrieved_memory.dict()
    elif hasattr(retrieved_memory, "model_dump") and callable(getattr(retrieved_memory, "model_dump")):
        retrieved_memory_dict = retrieved_memory.model_dump()
    else:
        retrieved_memory_dict = retrieved_memory

    print(f"Retrieved memory: {json.dumps(retrieved_memory_dict, indent=2)}")

    # Search memories
    search_results = await memory_service.search_memories("solar jobs", "test_user", limit=5)

    # Convert search results to dict if needed
    serializable_results = []
    for result in search_results:
        if hasattr(result, "model_dump") and callable(getattr(result, "model_dump")):
            serializable_results.append(result.model_dump())
        elif hasattr(result, "dict") and callable(getattr(result, "dict")):
            serializable_results.append(result.dict())
        else:
            serializable_results.append(result)

    print(f"Search results: {json.dumps(serializable_results, indent=2)}")

    return memory_id

async def test_user_profile():
    """Test user profile operations"""
    print("\n=== Testing User Profile Operations ===")

    # Initialize memory service
    memory_service = MemoryService()

    # Create a test user profile
    test_profile = {
        "user_id": "test_user",
        "email": "test@example.com",
        "full_name": "Test User",
        "skills": ["Solar Installation", "Electrical Wiring", "Project Management"],
        "experience": [
            {
                "title": "Electrician",
                "company": "ABC Electric",
                "duration": "2018-2022",
                "description": "Installed and maintained electrical systems"
            }
        ],
        "education": [
            {
                "degree": "Associate's Degree",
                "institution": "Community College of Boston",
                "year": "2018",
                "field": "Electrical Technology"
            }
        ],
        "certifications": ["NABCEP PV Installation Professional"],
        "interests": ["Renewable Energy", "Sustainability"],
        "location": "Boston, MA",
        "is_veteran": True,
        "military_background": {
            "branch": "Army",
            "mos": "12B Combat Engineer",
            "years_served": "2010-2018"
        },
        "is_international": False,
        "is_ej_community": True,
        "ej_community_details": {
            "neighborhood": "Roxbury",
            "ej_criteria": ["minority", "income"]
        }
    }

    # Store user profile as a memory
    profile_memory = ClimateMemoryEntry(
        content=json.dumps(test_profile),
        user_id="test_user",
        category="user_profile",
        source="system",
        metadata={"profile_version": "1.0"}
    )

    # Add memory
    profile_memory_id = await memory_service.add_memory(profile_memory)
    print(f"Added profile memory with ID: {profile_memory_id}")

    # Search for user profile memories
    profile_memories = await memory_service.search_memories(
        "user_profile",
        "test_user",
        limit=1,
        categories=["user_profile"]
    )

    # Extract profile data
    if profile_memories:
        profile_memory = profile_memories[0]
        if isinstance(profile_memory, dict):
            profile_content = profile_memory.get("content", "{}")
        else:
            profile_content = getattr(profile_memory, "content", "{}")

        try:
            retrieved_profile = json.loads(profile_content)
            print(f"Retrieved profile: {json.dumps(retrieved_profile, indent=2)}")
        except json.JSONDecodeError:
            print(f"Error decoding profile content: {profile_content}")
            retrieved_profile = {}
    else:
        print("No user profile found")
        retrieved_profile = {}

    return retrieved_profile

async def test_ej_community_detection():
    """Test EJ community detection"""
    print("\n=== Testing EJ Community Detection ===")

    # Initialize memory service
    memory_service = MemoryService()

    # Test locations
    test_locations = [
        "Boston, MA",
        "Lawrence, MA",
        "Worcester, MA",
        "Cambridge, MA",
        "Springfield, MA"
    ]

    # Mock EJ community data
    ej_communities = {
        "boston": {
            "is_ej_community": True,
            "ej_criteria": ["minority", "income", "english_isolation"],
            "gateway_city": True
        },
        "lawrence": {
            "is_ej_community": True,
            "ej_criteria": ["minority", "income"],
            "gateway_city": True
        },
        "worcester": {
            "is_ej_community": True,
            "ej_criteria": ["income"],
            "gateway_city": True
        },
        "cambridge": {
            "is_ej_community": False,
            "ej_criteria": [],
            "gateway_city": False
        },
        "springfield": {
            "is_ej_community": True,
            "ej_criteria": ["minority", "income"],
            "gateway_city": True
        }
    }

    # Check each location
    for location in test_locations:
        # Extract city name
        city = location.split(",")[0].lower()

        # Get EJ data
        result = ej_communities.get(city, {
            "is_ej_community": False,
            "ej_criteria": [],
            "gateway_city": False
        })

        print(f"Location: {location}")
        print(f"EJ Community: {result.get('is_ej_community', False)}")
        print(f"EJ Criteria: {result.get('ej_criteria', [])}")
        print(f"Gateway City: {result.get('gateway_city', False)}")
        print()

async def test_resume_analysis():
    """Test resume analysis"""
    print("\n=== Testing Resume Analysis ===")

    # Initialize memory service
    memory_service = MemoryService()

    # Mock resume text
    resume_text = """
    JOHN DOE
    Boston, MA | john.doe@example.com | (555) 123-4567

    SUMMARY
    Experienced electrician with 5 years of experience in residential and commercial electrical systems.
    U.S. Army veteran with expertise in power distribution and electrical maintenance.

    EXPERIENCE
    Electrician, ABC Electric, Boston, MA (2018-2022)
    - Installed and maintained electrical systems for residential and commercial buildings
    - Performed troubleshooting and repairs on electrical equipment
    - Collaborated with construction teams on new building projects

    Combat Engineer, U.S. Army (2010-2018)
    - Operated and maintained power generation equipment
    - Installed electrical systems in field environments
    - Led a team of 5 engineers in various operations

    EDUCATION
    Associate's Degree in Electrical Technology
    Community College of Boston, 2018

    CERTIFICATIONS
    - NABCEP PV Installation Professional
    - OSHA 10-Hour Safety Certification

    SKILLS
    Electrical wiring, Solar PV installation, Blueprint reading, Power distribution, Team leadership
    """

    # Mock analysis results
    analysis = {
        "skills": [
            "Electrical Wiring",
            "Solar PV Installation",
            "Blueprint Reading",
            "Power Distribution",
            "Team Leadership",
            "Troubleshooting",
            "Equipment Maintenance"
        ],
        "experience": [
            {
                "title": "Electrician",
                "company": "ABC Electric",
                "duration": "2018-2022",
                "description": "Installed and maintained electrical systems for residential and commercial buildings"
            },
            {
                "title": "Combat Engineer",
                "company": "U.S. Army",
                "duration": "2010-2018",
                "description": "Operated and maintained power generation equipment"
            }
        ],
        "education": [
            {
                "degree": "Associate's Degree",
                "institution": "Community College of Boston",
                "year": "2018",
                "field": "Electrical Technology"
            }
        ],
        "certifications": [
            "NABCEP PV Installation Professional",
            "OSHA 10-Hour Safety Certification"
        ],
        "is_veteran": True,
        "military_background": {
            "branch": "Army",
            "role": "Combat Engineer",
            "years_served": "2010-2018"
        },
        "clean_energy_relevance": "high",
        "recommended_roles": [
            "Solar Installer",
            "Electrical Technician",
            "Energy Storage Technician",
            "Grid Technician"
        ]
    }

    # Store resume analysis as a memory
    resume_memory = ClimateMemoryEntry(
        content=resume_text,
        user_id="test_user",
        category="resume",
        source="user_upload",
        metadata={"analysis": analysis}
    )

    # Add memory
    memory_id = await memory_service.add_memory(resume_memory)
    print(f"Stored resume analysis with ID: {memory_id}")

    # Store skills as separate memories
    for skill in analysis.get("skills", []):
        skill_memory = ClimateMemoryEntry(
            content=f"Skill: {skill}",
            user_id="test_user",
            category="skill",
            source="resume_analysis",
            metadata={"skill_name": skill, "source": "resume"}
        )
        await memory_service.add_memory(skill_memory)

    print(f"Stored {len(analysis.get('skills', []))} skills as memories")

    return memory_id

async def main():
    """Main function to test Memory Service components"""
    print("=== Memory Service Test ===")

    # Test memory operations
    memory_id = await test_memory_operations()

    # Test user profile operations
    profile = await test_user_profile()

    # Test EJ community detection
    await test_ej_community_detection()

    # Test resume analysis
    resume_memory_id = await test_resume_analysis()

    print("\n=== Test Complete ===")
    print(f"Memory ID: {memory_id}")
    print(f"Resume Memory ID: {resume_memory_id}")
    print(f"User Profile ID: {profile.get('user_id')}")

if __name__ == "__main__":
    asyncio.run(main())
