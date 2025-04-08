#!/usr/bin/env python3
"""
Test script for Climate Economy Ecosystem Agent

This script tests the agent's responses and tool use by:
1. Simulating user queries
2. Processing the agent's responses
3. Collecting feedback
4. Testing different user personas (veteran, EJ community member, etc.)
"""

import os
import sys
import json
import asyncio
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import OpenAI for agent simulation
import openai
from openai import OpenAI

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai.api_key)

# Import tools
from lib.memory.memory_service import MemoryService, ClimateMemoryEntry, MemoryServiceError

try:
    from tools.military_skill_translator import translate_military_to_civilian_skills
except ImportError:
    # Mock function if the real one isn't available
    def translate_military_to_civilian_skills(mos):
        return {
            "mos": mos,
            "skills": ["Leadership", "Technical Skills", "Project Management"],
            "clean_energy_roles": ["Solar Installer", "Project Manager"]
        }

# Test user personas
PERSONAS = {
    "veteran": {
        "user_id": "veteran_user",
        "name": "John Doe",
        "background": "U.S. Army veteran with 8 years of service as a 12B Combat Engineer",
        "location": "Boston, MA",
        "is_veteran": True,
        "military_background": {
            "branch": "Army",
            "mos": "12B Combat Engineer",
            "years_served": "2010-2018"
        },
        "is_ej_community": False
    },
    "ej_community": {
        "user_id": "ej_community_user",
        "name": "Maria Rodriguez",
        "background": "Resident of Lawrence, MA with experience in community organizing",
        "location": "Lawrence, MA",
        "is_veteran": False,
        "is_ej_community": True,
        "ej_community_details": {
            "neighborhood": "Lawrence",
            "ej_criteria": ["minority", "income"]
        }
    },
    "international": {
        "user_id": "international_user",
        "name": "Raj Patel",
        "background": "Electrical engineer from India with 5 years of experience in power systems",
        "location": "Worcester, MA",
        "is_veteran": False,
        "is_international": True,
        "country_of_origin": "India",
        "is_ej_community": False
    }
}

# Test queries for each persona
QUERIES = {
    "veteran": [
        "What clean energy jobs are available for veterans in Massachusetts?",
        "How can my experience as a Combat Engineer translate to clean energy careers?",
        "Are there any training programs specifically for veterans in the clean energy sector?"
    ],
    "ej_community": [
        "What clean energy job opportunities are available in Lawrence?",
        "Are there any training programs for solar installation in my area?",
        "How can I get involved in community solar projects in my neighborhood?"
    ],
    "international": [
        "How can I transfer my electrical engineering skills from India to the clean energy sector in Massachusetts?",
        "What certifications do I need to work as an electrical engineer in clean energy here?",
        "Are there any companies in Worcester that hire international professionals for clean energy roles?"
    ]
}

async def setup_user_profile(persona_key):
    """Set up a user profile for testing"""
    print(f"\n=== Setting Up User Profile for {persona_key.capitalize()} ===")

    # Get persona data
    persona = PERSONAS[persona_key]

    # Initialize memory service
    memory_service = MemoryService()

    # Store user profile as a memory
    profile_memory = ClimateMemoryEntry(
        content=json.dumps(persona),
        user_id=persona["user_id"],
        category="user_profile",
        source="system",
        metadata={"profile_version": "1.0"}
    )

    # Add memory
    profile_memory_id = await memory_service.add_memory(profile_memory)
    print(f"Added profile memory with ID: {profile_memory_id}")

    return persona

async def simulate_agent_response(query, persona):
    """Simulate the agent's response to a query"""
    print(f"\n=== Simulating Agent Response ===")
    print(f"Query: {query}")
    print(f"Persona: {persona['name']} ({persona['background']})")

    # Create system message with persona context
    system_message = f"""
    You are the Massachusetts Clean Tech Ecosystem Assistant, an AI designed to help people find jobs,
    training, and resources in the clean energy sector in Massachusetts.

    User Information:
    - Name: {persona['name']}
    - Background: {persona['background']}
    - Location: {persona['location']}
    - Veteran Status: {'Veteran' if persona.get('is_veteran', False) else 'Not a veteran'}
    - EJ Community: {'Yes' if persona.get('is_ej_community', False) else 'No'}
    - International: {'Yes' if persona.get('is_international', False) else 'No'}

    Provide helpful, specific information about clean energy careers, training programs, and resources in Massachusetts.
    Focus on the user's specific background and needs.
    """

    # If the user is a veteran, use the military skill translator
    if persona.get("is_veteran", False) and "military_background" in persona:
        mos = persona["military_background"].get("mos", "")
        if mos:
            skill_translation = translate_military_to_civilian_skills(mos)
            system_message += f"\n\nMilitary Skill Translation:\n"
            system_message += f"- MOS: {skill_translation['mos']}\n"
            system_message += f"- Civilian Skills: {', '.join(skill_translation['skills'])}\n"
            system_message += f"- Recommended Clean Energy Roles: {', '.join(skill_translation['clean_energy_roles'])}\n"

    # If the user is from an EJ community, add relevant information
    if persona.get("is_ej_community", False) and "ej_community_details" in persona:
        system_message += f"\n\nEnvironmental Justice Community Information:\n"
        system_message += f"- Community: {persona['ej_community_details'].get('neighborhood', '')}\n"
        system_message += f"- EJ Criteria: {', '.join(persona['ej_community_details'].get('ej_criteria', []))}\n"
        system_message += f"- Provide information about programs specifically for EJ communities.\n"

    # Generate response using OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=800
        )

        agent_response = response.choices[0].message.content
        print(f"\nAgent Response:\n{agent_response}")

        return agent_response
    except Exception as e:
        print(f"Error generating agent response: {str(e)}")
        return "I apologize, but I'm having trouble generating a response right now."

async def collect_feedback(query, response, persona):
    """Collect feedback on the agent's response"""
    print(f"\n=== Collecting Feedback ===")

    # Simulate feedback collection
    # In a real system, this would come from the user
    feedback_score = 0

    # Check if response mentions Massachusetts
    if "Massachusetts" in response or "MA" in response:
        feedback_score += 1

    # Check if response is personalized to the user's background
    if persona.get("is_veteran", False) and ("veteran" in response.lower() or "military" in response.lower()):
        feedback_score += 1

    if persona.get("is_ej_community", False) and ("community" in response.lower() or "environmental justice" in response.lower()):
        feedback_score += 1

    if persona.get("is_international", False) and ("international" in response.lower() or "certification" in response.lower()):
        feedback_score += 1

    # Check if response mentions clean energy
    if "clean energy" in response.lower() or "renewable" in response.lower() or "solar" in response.lower():
        feedback_score += 1

    # Check if response mentions specific resources
    if "program" in response.lower() or "training" in response.lower() or "resource" in response.lower():
        feedback_score += 1

    # Normalize to 1-5 scale
    feedback_score = min(5, max(1, feedback_score))

    print(f"Feedback Score: {feedback_score}/5")

    # Store feedback
    feedback_data = {
        "id": str(uuid.uuid4()),
        "chat_id": str(uuid.uuid4()),
        "user_id": persona["user_id"],
        "message": response,
        "feedback_type": "rating",
        "feedback_score": feedback_score,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # In a real system, this would be stored in the database
    print(f"Feedback stored: {json.dumps(feedback_data, indent=2)}")

    return feedback_data

async def test_persona(persona_key):
    """Test the agent with a specific persona"""
    print(f"\n=== Testing {persona_key.capitalize()} Persona ===")

    # Set up user profile
    persona = await setup_user_profile(persona_key)

    # Get queries for this persona
    queries = QUERIES[persona_key]

    # Process each query
    feedback_data = []
    for query in queries:
        # Simulate agent response
        response = await simulate_agent_response(query, persona)

        # Collect feedback
        feedback = await collect_feedback(query, response, persona)
        feedback_data.append(feedback)

    return feedback_data

async def main():
    """Main function to test the agent"""
    print("=== Climate Economy Ecosystem Agent Test ===")

    # Test each persona
    all_feedback = {}
    for persona_key in PERSONAS.keys():
        feedback_data = await test_persona(persona_key)
        all_feedback[persona_key] = feedback_data

    # Print summary
    print("\n=== Test Summary ===")
    for persona_key, feedback_list in all_feedback.items():
        avg_score = sum(f["feedback_score"] for f in feedback_list) / len(feedback_list)
        print(f"{persona_key.capitalize()} Persona: Average Feedback Score = {avg_score:.2f}/5")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main())
