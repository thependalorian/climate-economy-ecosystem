#!/usr/bin/env python3
"""
Credential Evaluator for International Professionals

This script evaluates foreign credentials and maps them to US equivalents,
focused specifically on clean energy careers in Massachusetts.

Usage:
    python credential_evaluator.py "Bachelor of Engineering, Nigeria" "Electrical Engineering"
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
import logging

import openai
from openai import OpenAI
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database of common international credential equivalencies
# This serves as a fallback if the AI evaluation fails
CREDENTIAL_EQUIVALENCY_MAP = {
    # Format: "Country:Degree" -> US Equivalent
    "Nigeria:Bachelor of Engineering": "Bachelor of Science in Engineering",
    "Nigeria:HND": "Associate Degree",
    "India:Bachelor of Technology": "Bachelor of Science in Engineering",
    "India:Bachelor of Engineering": "Bachelor of Science in Engineering",
    "Ghana:Bachelor of Science": "Bachelor of Science",
    "Kenya:Bachelor of Technology": "Bachelor of Science",
    "China:Bachelor's Degree": "Bachelor's Degree",
    "Brazil:Bacharelado": "Bachelor's Degree",
    "Mexico:Licenciatura": "Bachelor's Degree",
    "UK:Master of Engineering": "Master of Science in Engineering",
    "Germany:Diplom-Ingenieur": "Master of Science in Engineering",
    "France:Diplôme d'Ingénieur": "Master of Science in Engineering",
    "Philippines:Bachelor of Science": "Bachelor of Science",
    "South Africa:Bachelor of Engineering": "Bachelor of Science in Engineering"
}

# Mapping of education systems to US equivalents
EDUCATION_SYSTEMS = {
    "UK": {
        "A-Levels": "High School Diploma with Advanced Placement",
        "Higher National Diploma": "Associate Degree",
        "Bachelor's Degree": "Bachelor's Degree (4 years)",
        "Master's Degree": "Master's Degree",
        "PhD": "PhD"
    },
    "India": {
        "Higher Secondary Certificate": "High School Diploma",
        "Diploma": "Associate Degree",
        "Bachelor's Degree": "Bachelor's Degree",
        "Master's Degree": "Master's Degree",
        "PhD": "PhD"
    },
    "Nigeria": {
        "WAEC/NECO": "High School Diploma",
        "National Diploma (ND)": "Associate Degree (partial)",
        "Higher National Diploma (HND)": "Associate Degree",
        "Bachelor's Degree": "Bachelor's Degree",
        "Master's Degree": "Master's Degree",
        "PhD": "PhD"
    }
}

# Clean energy relevant fields and their US equivalents
FIELD_EQUIVALENCY = {
    "Electrical Engineering": ["Electrical Engineering", "Power Systems Engineering"],
    "Mechanical Engineering": ["Mechanical Engineering", "HVAC Engineering"],
    "Civil Engineering": ["Civil Engineering", "Structural Engineering"],
    "Energy Engineering": ["Energy Systems Engineering", "Renewable Energy Engineering"],
    "Environmental Engineering": ["Environmental Engineering", "Sustainability Engineering"],
    "Computer Engineering": ["Computer Engineering", "Software Engineering"],
    "Chemical Engineering": ["Chemical Engineering", "Process Engineering"]
}

def evaluate_credentials(country: str, credential: str, field: str = None) -> Dict[str, Any]:
    """
    Evaluate international credentials and map to US equivalents.
    
    Args:
        country: Country where credential was obtained
        credential: Degree or certification title
        field: Field of study or specialization
        
    Returns:
        Dict with evaluation results
    """
    try:
        # First check if we have a direct mapping
        key = f"{country}:{credential}"
        if key in CREDENTIAL_EQUIVALENCY_MAP:
            us_equivalent = CREDENTIAL_EQUIVALENCY_MAP[key]
            return format_evaluation_results(country, credential, field, us_equivalent)
        
        # If not a direct match, try education system lookup
        if country in EDUCATION_SYSTEMS:
            for foreign_cred, us_equiv in EDUCATION_SYSTEMS[country].items():
                if foreign_cred.lower() in credential.lower():
                    return format_evaluation_results(country, credential, field, us_equiv)
        
        # If no match found, use AI to evaluate
        return evaluate_with_ai(country, credential, field)
        
    except Exception as e:
        logger.error(f"Error evaluating credentials: {str(e)}")
        return {
            "country": country,
            "original_credential": credential,
            "field": field,
            "us_equivalent": "Unable to determine",
            "evaluation_notes": f"Error during evaluation: {str(e)}",
            "recommended_actions": ["Contact a professional credential evaluation service"],
            "confidence": 0
        }

def evaluate_with_ai(country: str, credential: str, field: str = None) -> Dict[str, Any]:
    """
    Use OpenAI to evaluate international credentials.
    
    Args:
        country: Country where credential was obtained
        credential: Degree or certification title
        field: Field of study or specialization
        
    Returns:
        Dict with evaluation results
    """
    try:
        # Create prompt for OpenAI
        prompt = f"""
        Evaluate the following international credential and provide the US equivalent, 
        specifically for the clean energy sector in Massachusetts:
        
        Country: {country}
        Credential: {credential}
        Field of Study: {field if field else 'Not specified'}
        
        Return a JSON object with the following structure:
        {{
            "us_equivalent": "US equivalent degree/certification",
            "evaluation_notes": "Notes about the equivalency",
            "recommended_actions": ["List of recommended actions for the credential holder"],
            "confidence": 0-100 confidence score,
            "additional_training_needed": ["List of additional training/certifications recommended"]
        }}
        
        Focus on clean energy sector requirements in Massachusetts.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a credential evaluation specialist with expertise in international academic and professional qualifications, especially for clean energy careers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse response
        response_text = response.choices[0].message.content
        evaluation = json.loads(response_text)
        
        # Format and return the results
        return format_evaluation_results(
            country, 
            credential, 
            field, 
            evaluation.get("us_equivalent", "Unable to determine"),
            evaluation.get("evaluation_notes", ""),
            evaluation.get("recommended_actions", []),
            evaluation.get("confidence", 50),
            evaluation.get("additional_training_needed", [])
        )
            
    except Exception as e:
        logger.error(f"Error evaluating with AI: {str(e)}")
        return {
            "country": country,
            "original_credential": credential,
            "field": field,
            "us_equivalent": "Unable to determine",
            "evaluation_notes": "Error during AI evaluation. Please try again or contact a professional credential evaluation service.",
            "recommended_actions": ["Contact a professional credential evaluation service"],
            "confidence": 0
        }

def format_evaluation_results(
    country: str, 
    credential: str, 
    field: str, 
    us_equivalent: str,
    evaluation_notes: str = "",
    recommended_actions: List[str] = None,
    confidence: int = 75,
    additional_training: List[str] = None
) -> Dict[str, Any]:
    """
    Format credential evaluation results.
    
    Args:
        country: Country where credential was obtained
        credential: Original credential
        field: Field of study
        us_equivalent: US equivalent degree/certification
        evaluation_notes: Notes about the equivalency
        recommended_actions: List of recommended actions
        confidence: Confidence score (0-100)
        additional_training: List of additional training needed
        
    Returns:
        Dict with formatted evaluation results
    """
    if recommended_actions is None:
        recommended_actions = [
            "Get credential evaluated by a NACES-member organization",
            "Check Massachusetts professional licensing requirements"
        ]
        
    if additional_training is None:
        additional_training = []
        
    # Add field-specific recommendations
    if field and field in FIELD_EQUIVALENCY:
        us_fields = FIELD_EQUIVALENCY[field]
        field_note = f"Your {field} background is most similar to {', '.join(us_fields)} in the US system."
        
        if not evaluation_notes:
            evaluation_notes = field_note
        else:
            evaluation_notes += " " + field_note
    
    # Clean energy specific recommendations
    clean_energy_certifications = [
        "NABCEP (North American Board of Certified Energy Practitioners) certification",
        "BPI (Building Performance Institute) certification",
        "LEED (Leadership in Energy and Environmental Design) certification"
    ]
    
    # Add clean energy certifications if the field is relevant
    relevant_fields = [
        "Electrical", "Engineering", "Energy", "Environmental", 
        "Mechanical", "Civil", "Construction", "Architecture"
    ]
    
    if field and any(term in field for term in relevant_fields) and not additional_training:
        additional_training = clean_energy_certifications
        
    return {
        "country": country,
        "original_credential": credential,
        "field": field,
        "us_equivalent": us_equivalent,
        "evaluation_notes": evaluation_notes,
        "recommended_actions": recommended_actions,
        "confidence": confidence,
        "additional_training_needed": additional_training,
        "massachusetts_specific": {
            "licensing_required": is_licensing_required(field),
            "acceptance_level": get_acceptance_level(us_equivalent),
            "clean_energy_relevance": get_clean_energy_relevance(field)
        }
    }

def is_licensing_required(field: Optional[str]) -> bool:
    """
    Determine if licensing is required for the field in Massachusetts.
    
    Args:
        field: Field of study
        
    Returns:
        Boolean indicating if licensing is required
    """
    if not field:
        return False
        
    licensed_fields = [
        "Engineering", "Architecture", "Electrician", "HVAC", "Plumbing",
        "Construction Supervisor", "Home Inspector"
    ]
    
    return any(licensed_field in field for licensed_field in licensed_fields)

def get_acceptance_level(us_equivalent: str) -> str:
    """
    Determine how widely accepted the credential is in Massachusetts.
    
    Args:
        us_equivalent: US equivalent credential
        
    Returns:
        Acceptance level (High/Medium/Low)
    """
    high_acceptance = ["Bachelor", "Master", "PhD", "Professional Engineer"]
    medium_acceptance = ["Associate", "Certificate", "Diploma"]
    
    if any(term in us_equivalent for term in high_acceptance):
        return "High"
    elif any(term in us_equivalent for term in medium_acceptance):
        return "Medium"
    else:
        return "Low"

def get_clean_energy_relevance(field: Optional[str]) -> str:
    """
    Determine relevance of the field to clean energy sector.
    
    Args:
        field: Field of study
        
    Returns:
        Relevance level (High/Medium/Low)
    """
    if not field:
        return "Unknown"
        
    high_relevance = [
        "Renewable Energy", "Solar", "Wind", "Energy", "Electrical", 
        "Power Systems", "Energy Storage", "Smart Grid"
    ]
    
    medium_relevance = [
        "Mechanical", "Civil", "Environmental", "Sustainability", 
        "Construction", "HVAC", "Building Science"
    ]
    
    low_relevance = [
        "Computer Science", "IT", "Software", "Business", "Management",
        "Marketing", "Finance", "Economics"
    ]
    
    if any(term.lower() in field.lower() for term in high_relevance):
        return "High"
    elif any(term.lower() in field.lower() for term in medium_relevance):
        return "Medium"
    elif any(term.lower() in field.lower() for term in low_relevance):
        return "Low"
    else:
        return "Unknown"

def get_ma_credential_resources() -> List[Dict[str, str]]:
    """
    Get Massachusetts-specific credential evaluation resources.
    
    Returns:
        List of credential evaluation resources
    """
    return [
        {
            "name": "Massachusetts Department of Professional Licensure",
            "url": "https://www.mass.gov/orgs/division-of-professional-licensure",
            "description": "Official state agency for professional licensing"
        },
        {
            "name": "World Education Services (WES)",
            "url": "https://www.wes.org/",
            "description": "NACES-member credential evaluation service"
        },
        {
            "name": "Educational Credential Evaluators (ECE)",
            "url": "https://www.ece.org/",
            "description": "NACES-member credential evaluation service"
        },
        {
            "name": "MassHire Career Centers",
            "url": "https://www.mass.gov/masshire-career-centers",
            "description": "Career services including credential guidance"
        },
        {
            "name": "Massachusetts Clean Energy Center",
            "url": "https://www.masscec.com/",
            "description": "Clean energy industry support and workforce development"
        }
    ]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python credential_evaluator.py <country> <credential> [field]", file=sys.stderr)
        sys.exit(1)
        
    country = sys.argv[1]
    credential = sys.argv[2]
    field = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Evaluate credentials
    results = evaluate_credentials(country, credential, field)
    
    # Add Massachusetts resources
    results["resources"] = get_ma_credential_resources()
    
    # Print results as JSON
    print(json.dumps(results, indent=2)) 