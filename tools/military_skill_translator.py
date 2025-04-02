#!/usr/bin/env python3
"""
Military Skill Translator for Climate Economy Assistant

This script translates military occupational specialties (MOS) and
military experience into equivalent civilian skills relevant to
clean energy careers in Massachusetts.

Usage:
    python military_skill_translator.py "11B Infantry"
"""

import os
import sys
import json
from typing import Dict, List, Any

import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Military to civilian skill mappings for common MOS codes
# This serves as a fallback if the AI translation fails
MOS_SKILL_MAP = {
    # Army
    "11B": ["Team Leadership", "Security Operations", "Equipment Maintenance", "Risk Assessment", "Critical Decision Making"],
    "12B": ["Construction", "Electrical Systems", "Heavy Equipment Operation", "Project Management", "Blueprint Reading"],
    "12K": ["Electrical Work", "Power Distribution", "Generator Maintenance", "Electrical Safety", "Troubleshooting"],
    "12R": ["Electrical Systems", "Interior Wiring", "Power Generation", "System Inspection", "Technical Compliance"],
    "13B": ["Heavy Equipment Operation", "Technical Maintenance", "Team Coordination", "Inventory Management", "Safety Procedures"],
    "15R": ["Helicopter Maintenance", "Electronic Systems", "Mechanical Repair", "Quality Control", "Technical Documentation"],
    "25B": ["IT Systems", "Network Administration", "Technical Troubleshooting", "Systems Installation", "User Support"],
    "31B": ["Security Operations", "Emergency Response", "Report Documentation", "Team Leadership", "Risk Assessment"],
    "35F": ["Data Analysis", "Research", "Report Writing", "Briefing", "Critical Thinking"],
    "88M": ["Vehicle Operation", "Route Planning", "Logistics Management", "Safety Protocols", "Equipment Maintenance"],
    "91B": ["Mechanical Repair", "Diagnostics", "Technical Documentation", "Safety Procedures", "Quality Control"],
    
    # Navy
    "ET": ["Electronics", "Technical Troubleshooting", "System Testing", "Circuit Analysis", "Equipment Calibration"],
    "EM": ["Electrical Maintenance", "Power Generation", "System Testing", "Technical Documentation", "Safety Procedures"],
    "MM": ["Mechanical Systems", "Preventative Maintenance", "Equipment Repair", "Fluid Systems", "Technical Documentation"],
    "CE": ["Construction", "Project Planning", "Blueprint Reading", "Heavy Equipment Operation", "Quality Control"],
    "CM": ["Construction", "Carpentry", "Structural Work", "Project Planning", "Team Coordination"],
    "HT": ["Welding", "Metalworking", "Technical Documentation", "Quality Control", "Equipment Maintenance"],
    "IS": ["Data Analysis", "Research", "Report Writing", "Briefing", "Critical Thinking"],
    
    # Air Force
    "1A8": ["Communication Systems", "Data Analysis", "Report Documentation", "Security Procedures", "Attention to Detail"],
    "2A5": ["Aircraft Maintenance", "Electrical Systems", "Technical Documentation", "Quality Control", "Troubleshooting"],
    "2A6": ["Aerospace Systems", "Electronic Maintenance", "Technical Documentation", "Equipment Testing", "Quality Assurance"],
    "3D1": ["IT Systems", "Network Administration", "Cybersecurity", "Technical Support", "System Installation"],
    "3E0": ["Electrical Systems", "Power Generation", "System Testing", "Safety Procedures", "Technical Documentation"],
    "3E4": ["HVAC Systems", "Refrigeration", "Equipment Maintenance", "System Testing", "Technical Documentation"],
    
    # Marines
    "0311": ["Team Leadership", "Security Operations", "Equipment Maintenance", "Risk Assessment", "Critical Decision Making"],
    "1141": ["Electrical Systems", "Power Generation", "System Testing", "Technical Documentation", "Safety Procedures"],
    "1142": ["HVAC Systems", "Refrigeration", "Equipment Maintenance", "System Testing", "Technical Documentation"],
    "1171": ["Water Systems", "Environmental Systems", "Equipment Maintenance", "Technical Documentation", "Safety Procedures"],
    "1341": ["Engine Repair", "Preventative Maintenance", "Diagnostics", "Technical Documentation", "Quality Control"],
    "1345": ["Heavy Equipment Operation", "Preventative Maintenance", "Project Planning", "Safety Procedures", "Team Coordination"],
    "1391": ["Administration", "Inventory Management", "Technical Documentation", "Process Improvement", "Quality Control"]
}

def translate_military_to_civilian_skills(mos: str) -> Dict[str, Any]:
    """
    Translate military MOS and experience into civilian skills.
    
    Args:
        mos: Military Occupational Specialty code or description
        
    Returns:
        Dict with translated skills
    """
    try:
        # First check if this is a known MOS code
        for mos_code, skills in MOS_SKILL_MAP.items():
            if mos_code in mos:
                return {
                    "mos": mos,
                    "skills": skills,
                    "clean_energy_roles": get_clean_energy_roles_for_skills(skills)
                }
        
        # If not a simple match, use AI to translate
        skills = translate_with_ai(mos)
        clean_energy_roles = get_clean_energy_roles_for_skills(skills)
        
        return {
            "mos": mos,
            "skills": skills,
            "clean_energy_roles": clean_energy_roles
        }
        
    except Exception as e:
        print(f"Error translating military skills: {str(e)}", file=sys.stderr)
        return {
            "mos": mos,
            "skills": [],
            "clean_energy_roles": []
        }

def translate_with_ai(mos: str) -> List[str]:
    """
    Use OpenAI to translate military experience to civilian skills.
    
    Args:
        mos: Military Occupational Specialty code or description
        
    Returns:
        List of civilian skills
    """
    try:
        # Create prompt for OpenAI
        prompt = f"""
        Translate the following military MOS or experience into civilian skills 
        that would be relevant for clean energy careers. Focus on technical, 
        management, and transferable skills that apply to renewable energy, 
        energy efficiency, grid modernization, and related clean energy fields.
        
        Military MOS/Experience: {mos}
        
        Return ONLY a JSON array of skills (no explanation text), like this:
        ["Skill 1", "Skill 2", "Skill 3", etc.]
        
        Aim for 10-15 specific and relevant skills.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a military-to-civilian skill translator focused on clean energy careers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse response
        response_text = response.choices[0].message.content
        skills_json = json.loads(response_text)
        
        # Extract skills from response
        if isinstance(skills_json, list):
            return skills_json
        elif isinstance(skills_json, dict) and "skills" in skills_json:
            return skills_json["skills"]
        else:
            # Try to extract any array in the response
            for key, value in skills_json.items():
                if isinstance(value, list):
                    return value
            
            return []
            
    except Exception as e:
        print(f"Error translating with AI: {str(e)}", file=sys.stderr)
        return []

def get_clean_energy_roles_for_skills(skills: List[str]) -> List[str]:
    """
    Recommend clean energy roles based on skills.
    
    Args:
        skills: List of civilian skills
        
    Returns:
        List of recommended clean energy roles
    """
    # Map of skills to potential roles
    SKILL_TO_ROLE_MAP = {
        "Electrical": ["Solar Installer", "Grid Technician", "Energy Storage Technician"],
        "Electrical Systems": ["Solar Installer", "Grid Technician", "Energy Storage Technician"],
        "Electrical Work": ["Solar Installer", "Grid Technician", "Energy Storage Technician"],
        "Power Generation": ["Solar Installer", "Wind Turbine Technician", "Grid Technician"],
        "HVAC": ["HVAC Technician", "Energy Auditor", "Building Performance Specialist"],
        "Mechanical": ["Wind Turbine Technician", "HVAC Technician", "Solar Installer"],
        "Mechanical Systems": ["Wind Turbine Technician", "HVAC Technician", "Solar Installer"],
        "Mechanical Repair": ["Wind Turbine Technician", "HVAC Technician", "Maintenance Technician"],
        "Construction": ["Weatherization Technician", "Solar Installer", "Construction Manager"],
        "Project Management": ["Project Manager", "Construction Manager", "Installation Supervisor"],
        "Leadership": ["Team Lead", "Crew Supervisor", "Project Manager"],
        "Team Leadership": ["Team Lead", "Crew Supervisor", "Project Manager"],
        "Safety": ["Safety Coordinator", "Quality Control Specialist", "Site Supervisor"],
        "Safety Procedures": ["Safety Coordinator", "Quality Control Specialist", "Site Supervisor"],
        "Quality Control": ["Quality Control Specialist", "Inspector", "Commissioning Technician"],
        "Heavy Equipment": ["Heavy Equipment Operator", "Construction Manager", "Site Preparation Specialist"],
        "Heavy Equipment Operation": ["Heavy Equipment Operator", "Construction Manager", "Site Preparation Specialist"],
        "Logistics": ["Supply Chain Specialist", "Warehouse Manager", "Fleet Manager"],
        "Logistics Management": ["Supply Chain Specialist", "Warehouse Manager", "Fleet Manager"],
        "Technical Documentation": ["Technical Writer", "Quality Control Specialist", "Compliance Specialist"],
        "Data Analysis": ["Energy Analyst", "Performance Monitoring Specialist", "Building Systems Analyst"],
        "Planning": ["Project Planner", "Logistics Coordinator", "Project Manager"],
        "Communication": ["Customer Service Representative", "Sales Associate", "Community Outreach Specialist"],
        "Leadership": ["Team Lead", "Supervisor", "Manager"],
        "Problem Solving": ["Technician", "Field Service Specialist", "System Designer"],
        "Risk Assessment": ["Safety Officer", "Risk Manager", "Project Manager"],
    }
    
    recommended_roles = set()
    
    # Match skills to roles
    for skill in skills:
        for key, roles in SKILL_TO_ROLE_MAP.items():
            if key.lower() in skill.lower():
                for role in roles:
                    recommended_roles.add(role)
    
    return list(recommended_roles)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a military MOS or description", file=sys.stderr)
        sys.exit(1)
        
    mos = sys.argv[1]
    
    # Translate military skills
    results = translate_military_to_civilian_skills(mos)
    
    # Print results as JSON
    print(json.dumps(results)) 