#!/usr/bin/env python3
"""
Resume Processor for Massachusetts Climate Economy Assistant

This script processes resume text to extract skills, experience, and education
information. It uses keyword matching and pattern recognition to identify
clean energy related skills and experience.

Usage:
    python resume_processor.py resume_file.txt
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Clean energy skills database
CLEAN_ENERGY_SKILLS = [
    # Technical Skills
    "Solar PV installation", "Wind turbine maintenance", "HVAC", "Energy auditing",
    "Building automation", "Energy modeling", "Weatherization", "Insulation",
    "Heat pump installation", "Smart grid", "Energy storage", "Battery technology",
    "EV charging infrastructure", "Electrical work", "Building science",
    "Load calculations", "Energy management", "Building commissioning",
    "Net zero design", "Passive house", "LEED", "Energy Star", "Grid integration",
    "Power electronics", "Building performance testing", "Blower door testing",
    "Thermography", "Renewable energy", "Microgrid", "Distributed energy",
    
    # Software/Analysis Skills
    "Energy simulation", "BIM", "AutoCAD", "SketchUp", "Revit", "EnergyPlus",
    "OpenStudio", "HOMER", "RETScreen", "PVsyst", "SAM", "Excel energy models",
    "Data analysis", "Energy monitoring", "Power systems modeling", "SCADA",
    "GridLAB-D", "Energy accounting", "Life cycle assessment", "Carbon accounting",
    
    # Business/Management Skills
    "Project management", "Energy procurement", "Grant writing", "Energy policy",
    "Incentive applications", "Sustainability reporting", "Energy contracts",
    "Carbon markets", "Clean energy finance", "Community engagement",
    "Customer acquisition", "Client management", "Team leadership",
    "Energy sales", "Business development", "Program management",
    "Stakeholder engagement", "Energy efficiency programs", "Utility coordination",
    
    # Certifications
    "BPI", "RESNET", "NABCEP", "AEE", "CEM", "LEED GA", "LEED AP", "NATE",
    "ASHRAE", "EPA 608", "OSHA", "Professional Engineer", "PMP", "EnergyStar",
    "Net Zero Certification", "Passive House"
]

def process_resume(file_path: str) -> Dict[str, Any]:
    """
    Process resume file to extract skills, experience, and education.
    
    Args:
        file_path: Path to resume file
        
    Returns:
        Dict containing extracted information
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
            
        # Process with both keyword-based and AI approaches
        keyword_results = extract_skills_keyword_based(resume_text)
        ai_results = extract_information_with_ai(resume_text)
        
        # Combine results (AI results take precedence)
        combined_results = {
            "skills": list(set(keyword_results["skills"] + ai_results["skills"])),
            "experience": ai_results["experience"],
            "education": ai_results["education"],
            "summary": ai_results.get("summary", "")
        }
        
        return combined_results
        
    except Exception as e:
        print(f"Error processing resume: {str(e)}", file=sys.stderr)
        return {
            "skills": [],
            "experience": [],
            "education": []
        }

def extract_skills_keyword_based(resume_text: str) -> Dict[str, List[str]]:
    """
    Extract skills from resume text using keyword matching.
    
    Args:
        resume_text: Resume text content
        
    Returns:
        Dict containing extracted skills
    """
    skills = []
    
    # Normalize text
    text = resume_text.lower()
    
    # Match skills from our database
    for skill in CLEAN_ENERGY_SKILLS:
        if skill.lower() in text or re.search(r'\b' + re.escape(skill.lower()) + r'\b', text):
            skills.append(skill)
    
    # Look for common skill section indicators
    skill_sections = [
        r'skills:.*?(?=\n\n)',
        r'technical skills:.*?(?=\n\n)',
        r'qualifications:.*?(?=\n\n)',
        r'competencies:.*?(?=\n\n)',
        r'proficient in:.*?(?=\n\n)',
    ]
    
    for pattern in skill_sections:
        section_match = re.search(pattern, text, re.DOTALL)
        if section_match:
            section_text = section_match.group(0)
            # Find skill keywords in the section
            potential_skills = re.findall(r'[\w\s\-\+\#\/]+(?:,|\n|$)', section_text)
            for skill in potential_skills:
                skill = skill.strip(', \n').strip()
                if skill and len(skill) > 2 and skill not in ["skills", "include", "including", "and"]:
                    skills.append(skill)
    
    return {
        "skills": list(set(skills))
    }

def extract_information_with_ai(resume_text: str) -> Dict[str, Any]:
    """
    Extract information from resume text using OpenAI.
    
    Args:
        resume_text: Resume text content
        
    Returns:
        Dict containing extracted information
    """
    try:
        # Truncate resume text if too long
        if len(resume_text) > 12000:
            resume_text = resume_text[:12000]
        
        # Create prompt for OpenAI
        prompt = f"""
        Extract relevant information from this resume. Focus on skills and experience related to clean energy, sustainability, 
        climate tech, and related fields. Format the output as JSON with the following structure:
        {{
            "skills": ["skill1", "skill2", ...],
            "experience": [
                {{"title": "Job Title", "company": "Company Name", "dates": "Start-End", "description": "Brief description"}},
                ...
            ],
            "education": [
                {{"degree": "Degree", "institution": "Institution", "dates": "Start-End", "field": "Field of Study"}},
                ...
            ],
            "summary": "Brief professional summary"
        }}
        
        For skills, be comprehensive and include both technical and soft skills, especially those relevant to clean energy.
        
        RESUME TEXT:
        {resume_text}
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled resume parser focused on clean energy careers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse response
        response_text = response.choices[0].message.content
        parsed_result = json.loads(response_text)
        
        # Ensure expected keys exist
        for key in ["skills", "experience", "education", "summary"]:
            if key not in parsed_result:
                parsed_result[key] = [] if key != "summary" else ""
        
        return parsed_result
        
    except Exception as e:
        print(f"Error extracting information with AI: {str(e)}", file=sys.stderr)
        return {
            "skills": [],
            "experience": [],
            "education": [],
            "summary": ""
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide resume file path", file=sys.stderr)
        sys.exit(1)
        
    resume_file = sys.argv[1]
    if not os.path.exists(resume_file):
        print(f"File not found: {resume_file}", file=sys.stderr)
        sys.exit(1)
    
    # Process resume
    results = process_resume(resume_file)
    
    # Print JSON results
    print(json.dumps(results)) 