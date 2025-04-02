#!/usr/bin/env python3
"""
International Prompts for Climate Economy Ecosystem Assistant

This module contains specialized prompts for working with international
professionals seeking to enter the Massachusetts clean energy sector.
"""

from typing import Dict, Any, List, Optional

# System prompt for credential evaluation
CREDENTIAL_EVALUATION_SYSTEM_PROMPT = """
You are an expert credential evaluator specializing in helping international professionals 
transition into the Massachusetts clean energy sector. Your expertise includes understanding 
educational equivalencies between countries, identifying credential gaps, and providing 
concrete steps for credential recognition.

Focus on providing accurate, actionable information about:
1. How international credentials map to US equivalents
2. Massachusetts-specific licensing and certification requirements
3. Credential evaluation services and processes
4. Bridging educational or credential gaps

Be honest about challenges international professionals might face but maintain an 
encouraging tone and highlight pathways to overcome these challenges.
"""

# Prompt for assessing equivalency
def get_credential_equivalency_prompt(
    country: str, 
    credential: str, 
    field: str, 
    years_experience: Optional[int] = None
) -> str:
    """
    Generate prompt for credential equivalency assessment.
    
    Args:
        country: Country where credentials were obtained
        credential: Degree or certification name
        field: Field of study or expertise
        years_experience: Years of professional experience
        
    Returns:
        Formatted prompt
    """
    experience_text = f"with {years_experience} years of professional experience" if years_experience else ""
    
    return f"""
    Please evaluate the following international credential:
    
    Country: {country}
    Credential: {credential}
    Field: {field}
    {experience_text}
    
    Provide:
    1. The US equivalent of this credential in the clean energy context
    2. Whether this would be recognized by Massachusetts employers
    3. Any licensing or certification requirements in Massachusetts
    4. Specific credential evaluation services the person should consider
    5. Any additional education or training recommended
    
    Focus specifically on Massachusetts clean energy sector requirements and opportunities.
    """

# Prompt for credential pathways
def get_credential_pathway_prompt(evaluation_results: Dict[str, Any]) -> str:
    """
    Generate prompt for credential pathway recommendations.
    
    Args:
        evaluation_results: Results from credential evaluation
        
    Returns:
        Formatted prompt
    """
    return f"""
    Based on the following credential evaluation:
    
    Original Credential: {evaluation_results.get('original_credential')}
    US Equivalent: {evaluation_results.get('us_equivalent')}
    Field: {evaluation_results.get('field')}
    
    Provide a step-by-step pathway for this international professional to:
    
    1. Get their credentials formally recognized in Massachusetts
    2. Address any identified credential gaps
    3. Obtain necessary licenses or certifications for the clean energy sector
    4. Find employment opportunities that match their background
    
    Include specific Massachusetts resources, timelines, and approximate costs where possible.
    Focus on practical, actionable steps with highest priority items first.
    """

# Prompt for clean energy career matching
def get_career_matching_prompt(
    country: str,
    field: str,
    skills: List[str],
    desired_sector: Optional[str] = None
) -> str:
    """
    Generate prompt for matching international background to clean energy careers.
    
    Args:
        country: Country of origin
        field: Field of expertise
        skills: List of skills
        desired_sector: Desired clean energy sector
        
    Returns:
        Formatted prompt
    """
    sector_text = f"with interest in the {desired_sector} sector" if desired_sector else ""
    skills_text = ", ".join(skills)
    
    return f"""
    Match the following international professional's background to Massachusetts clean energy careers:
    
    Country of Origin: {country}
    Field of Expertise: {field}
    Skills: {skills_text}
    {sector_text}
    
    Provide:
    1. The 3-5 most suitable clean energy roles in Massachusetts
    2. For each role: required credentials, alignment with their background, and potential salary range
    3. Any Massachusetts-specific advantages or challenges they might face
    4. Companies in Massachusetts that might value international experience in this field
    
    Focus on realistic opportunities based on their background and the Massachusetts clean energy landscape.
    """

# Prompt for education pathway
def get_education_pathway_prompt(profile: Dict[str, Any]) -> str:
    """
    Generate prompt for education pathways.
    
    Args:
        profile: User profile information
        
    Returns:
        Formatted prompt
    """
    credential = profile.get('international_credentials', {}).get('original_credential', 'Not specified')
    field = profile.get('international_credentials', {}).get('field', 'Not specified')
    country = profile.get('international_credentials', {}).get('country', 'Not specified')
    
    return f"""
    Recommend educational pathways for an international professional with the following background:
    
    Original Credential: {credential}
    Field: {field}
    Country: {country}
    
    Provide:
    1. Massachusetts educational institutions offering relevant programs
    2. Certificate or degree programs that would complement their background
    3. Online or part-time options that allow them to work while studying
    4. Approximate program durations and costs
    5. Any scholarships or financial aid specifically available to international students
    
    Focus on programs that would enhance their employability in the Massachusetts clean energy sector
    while building on their existing expertise.
    """

# Prompt for overcoming cultural barriers
CULTURAL_INTEGRATION_PROMPT = """
Provide guidance for an international professional entering the Massachusetts clean energy workforce on:

1. Workplace cultural norms in Massachusetts that might differ from their home country
2. Communication styles and expectations in American professional settings
3. Networking strategies that work well in the Massachusetts clean energy sector
4. Building professional credibility when coming from an international background
5. Resources and communities that can provide cultural and professional support

Offer practical, actionable advice that acknowledges challenges but emphasizes solutions
and opportunities. Focus on the Massachusetts clean energy sector specifically.
"""

# Prompt for resume adaptation
def get_resume_adaptation_prompt(country: str) -> str:
    """
    Generate prompt for resume adaptation.
    
    Args:
        country: Country of origin
        
    Returns:
        Formatted prompt
    """
    return f"""
    Provide specific guidance on adapting a resume from {country} for the Massachusetts clean energy job market:
    
    1. Key differences between {country} and US resume formats and expectations
    2. How to present international education and credentials effectively
    3. Skills and experiences to emphasize for clean energy employers
    4. Handling potential gaps in US experience or credentials
    5. Industry-specific terminology and keywords to include
    
    Include before/after examples of common resume sections and specific phrases or formats
    to use for maximum impact with Massachusetts clean energy employers.
    """

# Prompts for interview preparation
INTERVIEW_PREPARATION_PROMPT = """
Prepare an international professional for job interviews in the Massachusetts clean energy sector:

1. Common interview questions specific to clean energy roles
2. How to address questions about international credentials and experience
3. Cultural norms in Massachusetts interviews that might differ from other countries
4. How to demonstrate technical knowledge effectively
5. Questions the candidate should ask to show industry knowledge

Provide sample responses that demonstrate how to bridge international experience with
Massachusetts clean energy sector needs and values.
"""

# Comprehensive guidance prompt
COMPREHENSIVE_GUIDANCE_PROMPT = """
Provide comprehensive guidance for an international professional entering the Massachusetts clean energy workforce:

1. Credential evaluation and recognition process
2. Massachusetts-specific licensing and certification requirements
3. Job search strategies that work for international candidates
4. Cultural integration and workplace norms
5. Building a professional network in Massachusetts
6. Legal considerations regarding work authorization
7. Resources specifically for international professionals in clean energy

Focus on practical, actionable steps with a timeline and approximate costs where possible.
Emphasize pathways that have worked for other international professionals in similar situations.
"""
