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
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai

# Military to civilian skill mappings for common MOS codes with clean energy focus
# This serves as a fallback if the AI translation fails
MOS_SKILL_MAP = {
    # Army
    "11B": ["Team Leadership", "Security Operations", "Equipment Maintenance", "Risk Assessment", "Critical Decision Making", "Solar Site Security"],
    "12B": ["Construction", "Electrical Systems", "Heavy Equipment Operation", "Project Management", "Blueprint Reading", "Solar Panel Installation"],
    "12K": ["Electrical Work", "Power Distribution", "Generator Maintenance", "Electrical Safety", "Troubleshooting", "Microgrid Systems"],
    "12R": ["Electrical Systems", "Interior Wiring", "Power Generation", "System Inspection", "Technical Compliance", "Solar PV Installation"],
    "13B": ["Heavy Equipment Operation", "Technical Maintenance", "Team Coordination", "Inventory Management", "Safety Procedures", "Wind Turbine Construction"],
    "15R": ["Helicopter Maintenance", "Electronic Systems", "Mechanical Repair", "Quality Control", "Technical Documentation", "Wind Turbine Maintenance"],
    "25B": ["IT Systems", "Network Administration", "Technical Troubleshooting", "Systems Installation", "User Support", "Smart Grid Technology"],
    "31B": ["Security Operations", "Emergency Response", "Report Documentation", "Team Leadership", "Risk Assessment", "Energy Infrastructure Security"],
    "35F": ["Data Analysis", "Research", "Report Writing", "Briefing", "Critical Thinking", "Energy Policy Analysis"],
    "88M": ["Vehicle Operation", "Route Planning", "Logistics Management", "Safety Protocols", "Equipment Maintenance", "EV Fleet Management"],
    "91B": ["Mechanical Repair", "Diagnostics", "Technical Documentation", "Safety Procedures", "Quality Control", "EV Maintenance"],

    # Navy
    "ET": ["Electronics", "Technical Troubleshooting", "System Testing", "Circuit Analysis", "Equipment Calibration", "Solar Inverter Maintenance"],
    "EM": ["Electrical Maintenance", "Power Generation", "System Testing", "Technical Documentation", "Safety Procedures", "Renewable Energy Systems"],
    "MM": ["Mechanical Systems", "Preventative Maintenance", "Equipment Repair", "Fluid Systems", "Technical Documentation", "Geothermal Systems"],
    "CE": ["Construction", "Project Planning", "Blueprint Reading", "Heavy Equipment Operation", "Quality Control", "Green Building Construction"],
    "CM": ["Construction", "Carpentry", "Structural Work", "Project Planning", "Team Coordination", "Energy Efficient Construction"],

    # Air Force
    "1A1": ["Aircraft Maintenance", "System Testing", "Technical Documentation", "Safety Procedures", "Quality Control", "Wind Turbine Maintenance"],
    "1C8": ["Radar Systems", "Electronic Equipment", "Technical Troubleshooting", "System Testing", "Equipment Calibration", "Smart Grid Monitoring"],
    "2A6": ["Aircraft Maintenance", "Electronic Systems", "Mechanical Repair", "Quality Control", "Technical Documentation", "Battery Storage Systems"],
    "3E0": ["Electrical Systems", "Power Distribution", "Generator Maintenance", "Electrical Safety", "Troubleshooting", "Solar PV Systems"],
    "3E4": ["HVAC Systems", "Refrigeration", "System Testing", "Equipment Maintenance", "Energy Efficiency", "Building Energy Management"],

    # Marines
    "1141": ["Electrical Systems", "Power Generation", "System Testing", "Technical Documentation", "Safety Procedures", "Microgrid Installation"],
    "1142": ["Electrical Work", "Generator Maintenance", "Electrical Safety", "Troubleshooting", "Power Distribution", "Solar PV Systems"],
    "1161": ["Refrigeration", "HVAC Systems", "System Testing", "Equipment Maintenance", "Energy Efficiency", "Building Energy Management"],
    "1171": ["Water Treatment", "Environmental Systems", "Equipment Maintenance", "System Testing", "Technical Documentation", "Wastewater Energy Recovery"],
    "3521": ["Vehicle Maintenance", "Diagnostics", "Technical Documentation", "Safety Procedures", "Quality Control", "EV Maintenance"],
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
        that would be relevant for clean energy careers in Massachusetts. Focus on technical,
        management, and transferable skills that apply to:
        - Solar installation and maintenance
        - Wind energy technology
        - Energy efficiency and building retrofits
        - Electric vehicle technology and maintenance
        - Battery storage systems
        - Smart grid technology
        - Geothermal systems
        - Green building construction
        - Energy policy and project management

        Military MOS/Experience: {mos}

        Return ONLY a JSON array of skills (no explanation text), like this:
        ["Skill 1", "Skill 2", "Skill 3", etc.]

        Aim for 10-15 specific and relevant skills that directly translate to clean energy careers.
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
    # Map of skills to potential clean energy roles in Massachusetts
    SKILL_TO_ROLE_MAP = {
        # Electrical skills
        "Electrical": ["Solar Installer", "Grid Technician", "Energy Storage Technician", "EV Charging Station Installer"],
        "Electrical Systems": ["Solar Installer", "Grid Technician", "Energy Storage Technician", "Microgrid Specialist"],
        "Electrical Work": ["Solar Installer", "Grid Technician", "Energy Storage Technician", "Electrical Vehicle Technician"],
        "Power Generation": ["Solar Installer", "Wind Turbine Technician", "Grid Technician", "Microgrid Operator"],
        "Power Distribution": ["Grid Technician", "Substation Technician", "Utility Line Worker", "Smart Grid Specialist"],

        # HVAC and building systems
        "HVAC": ["HVAC Technician", "Energy Auditor", "Building Performance Specialist", "Geothermal Installer"],
        "HVAC Systems": ["HVAC Technician", "Energy Auditor", "Building Performance Specialist", "Geothermal Installer"],
        "Refrigeration": ["HVAC Technician", "Building Systems Specialist", "Cold Climate Heat Pump Installer"],
        "Energy Efficiency": ["Energy Auditor", "Weatherization Technician", "Building Performance Specialist"],

        # Mechanical skills
        "Mechanical": ["Wind Turbine Technician", "HVAC Technician", "Solar Installer", "Hydropower Technician"],
        "Mechanical Systems": ["Wind Turbine Technician", "HVAC Technician", "Solar Installer", "Biomass System Technician"],
        "Mechanical Repair": ["Wind Turbine Technician", "HVAC Technician", "Maintenance Technician", "EV Maintenance Specialist"],
        "Equipment Maintenance": ["Wind Turbine Technician", "Solar O&M Technician", "Facility Maintenance Specialist"],

        # Construction and installation
        "Construction": ["Weatherization Technician", "Solar Installer", "Construction Manager", "Green Building Specialist"],
        "Carpentry": ["Green Building Carpenter", "Weatherization Installer", "Solar Racking Installer"],
        "Welding": ["Wind Turbine Fabricator", "Solar Racking Installer", "Energy Infrastructure Welder"],
        "Blueprint Reading": ["Solar System Designer", "Green Building Specialist", "Energy Retrofit Planner"],

        # Management and leadership
        "Project Management": ["Clean Energy Project Manager", "Construction Manager", "Installation Supervisor", "Sustainability Program Manager"],
        "Leadership": ["Clean Energy Team Lead", "Crew Supervisor", "Project Manager", "Operations Manager"],
        "Team Leadership": ["Installation Team Lead", "Crew Supervisor", "Field Operations Manager"],

        # Safety and quality
        "Safety": ["Safety Coordinator", "Quality Control Specialist", "Site Supervisor", "OSHA Compliance Officer"],
        "Safety Procedures": ["Safety Coordinator", "Quality Control Specialist", "Site Supervisor", "Risk Management Specialist"],
        "Quality Control": ["Quality Control Specialist", "Inspector", "Commissioning Technician", "System Verification Specialist"],
        "Risk Assessment": ["Safety Officer", "Risk Manager", "Project Manager", "Environmental Compliance Specialist"],

        # Equipment operation
        "Heavy Equipment": ["Heavy Equipment Operator", "Construction Manager", "Site Preparation Specialist", "Wind Farm Construction Operator"],
        "Heavy Equipment Operation": ["Heavy Equipment Operator", "Construction Manager", "Site Preparation Specialist", "Solar Farm Developer"],

        # Logistics and supply chain
        "Logistics": ["Clean Energy Supply Chain Specialist", "Warehouse Manager", "Fleet Manager", "Materials Coordinator"],
        "Logistics Management": ["Supply Chain Specialist", "Warehouse Manager", "Fleet Manager", "Procurement Specialist"],
        "Inventory Management": ["Inventory Control Specialist", "Warehouse Manager", "Supply Chain Coordinator"],

        # Technical and analytical
        "Technical Documentation": ["Technical Writer", "Quality Control Specialist", "Compliance Specialist", "System Documentation Specialist"],
        "Data Analysis": ["Energy Analyst", "Performance Monitoring Specialist", "Building Systems Analyst", "Energy Data Scientist"],
        "Research": ["Clean Energy Researcher", "Technology Assessment Specialist", "Policy Analyst"],
        "Technical Troubleshooting": ["Field Service Technician", "System Diagnostics Specialist", "Technical Support Specialist"],

        # Planning and coordination
        "Planning": ["Project Planner", "Logistics Coordinator", "Project Manager", "Energy Program Planner"],
        "Team Coordination": ["Field Operations Coordinator", "Installation Team Lead", "Project Coordinator"],

        # Communication and customer service
        "Communication": ["Customer Service Representative", "Sales Associate", "Community Outreach Specialist", "Energy Educator"],
        "Report Writing": ["Technical Writer", "Energy Analyst", "Compliance Specialist", "Grant Writer"],
        "Briefing": ["Community Outreach Specialist", "Energy Educator", "Policy Advocate"],

        # Problem solving and critical thinking
        "Problem Solving": ["Field Service Technician", "System Designer", "Energy Efficiency Consultant", "Technical Support Specialist"],
        "Critical Thinking": ["Energy Analyst", "System Designer", "Policy Analyst", "Sustainability Consultant"],
        "Critical Decision Making": ["Project Manager", "Operations Manager", "System Designer", "Energy Program Manager"],

        # Clean energy specific
        "Solar PV Installation": ["Solar Installer", "PV System Designer", "Solar Project Manager"],
        "Wind Turbine Maintenance": ["Wind Turbine Technician", "Wind Farm Maintenance Manager", "Blade Repair Specialist"],
        "Smart Grid Technology": ["Smart Grid Technician", "Grid Modernization Specialist", "Energy Management System Specialist"],
        "EV Maintenance": ["Electric Vehicle Technician", "EV Charging Infrastructure Specialist", "Fleet Electrification Specialist"],
        "Microgrid Systems": ["Microgrid Technician", "Distributed Energy Resource Specialist", "Energy Storage Technician"],
        "Energy Infrastructure Security": ["Energy Security Specialist", "Critical Infrastructure Protection Officer", "Cybersecurity Specialist"],
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