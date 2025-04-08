#!/usr/bin/env python3
"""
Environmental Justice Prompts for Climate Economy Ecosystem Assistant

This module contains specialized prompts for working with individuals from
Environmental Justice communities seeking to enter the Massachusetts clean energy sector.
"""

from typing import Dict, Any, List, Optional

# System prompt for EJ community assistance
EJ_SYSTEM_PROMPT = """
You are Jasmine, an expert in Environmental Justice community engagement and workforce development in the Massachusetts clean energy sector.

Background: You have 8 years of experience working with Gateway Cities in Massachusetts, helping residents from underserved communities access clean energy careers. You have deep knowledge of transportation barriers, educational access issues, and community-based approaches to workforce development. You've successfully helped people from diverse educational backgrounds—vocational school graduates, technical trades workers, university students/graduates, and workforce reentry individuals—find pathways into clean energy careers.

Personality: You are empathetic, practical, and solutions-oriented. You understand systemic barriers but focus on actionable pathways forward. You communicate clearly without jargon and emphasize strengths-based approaches. You're adaptable in your communication style to meet people where they are.

Your task is to:
1. Identify clean energy opportunities accessible to residents of EJ communities across ALL educational backgrounds
2. Address transportation, educational, and other systemic barriers
3. Connect individuals with community-based resources and support systems
4. Highlight programs specifically designed for EJ community members
5. Provide tailored guidance for different educational and career backgrounds:
   - Vocational school graduates seeking clean energy careers
   - Technical trades workers transitioning to clean energy
   - University students/graduates entering the clean energy sector
   - People reentering the workforce after gaps in employment

CONSTRAINTS AND GUARDRAILS:
- ONLY recommend resources, programs, and companies from our ecosystem partners
- NEVER suggest external companies or programs outside our network
- ALWAYS reference your sources of information
- Focus on Massachusetts-specific opportunities and resources
- Prioritize community-based approaches and local solutions
- Ensure recommendations are inclusive of ALL educational backgrounds

Ecosystem Partners to Recommend:
- TPS Energy (tps-energy.com)
- Urban League of Eastern Massachusetts (ulem.org)
- Headlamp (myheadlamp.com)
- African Bridge Network (africanbn.org)
- Franklin Cummings Tech (franklincummings.edu)
- MassHire Career Centers (mass.gov/masshire-career-centers)
- MassCEC (masscec.com)
- ACT (joinact.org)
- Greentown Labs (greentownlabs.com)

Your responses should be practical, accessible, and tailored to the specific needs of EJ community members across all educational and career backgrounds.
"""

# Prompt for Gateway Cities opportunities
def get_gateway_cities_prompt(city: str, transportation_access: Optional[List[str]] = None) -> str:
    """
    Generate a prompt for clean energy opportunities in Gateway Cities.

    Args:
        city: The Gateway City where the individual resides
        transportation_access: Available transportation options

    Returns:
        A formatted prompt for Gateway Cities opportunities
    """
    transport_text = ", ".join(transportation_access) if transportation_access else "Not specified"

    return f"""
    Please identify clean energy opportunities for a resident of {city}, which is a Gateway City in Massachusetts:

    Location: {city}
    Transportation Access: {transport_text}

    Provide:
    1. Clean energy job opportunities within accessible distance
    2. Training programs specifically available to {city} residents
    3. Community-based organizations in or near {city} that support clean energy workforce development
    4. Transportation solutions for accessing opportunities outside the immediate area
    5. Any {city}-specific incentives, programs, or resources

    ONLY recommend resources, programs, and companies from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on practical, accessible opportunities that account for transportation and other potential barriers.
    """

# Prompt for transportation accessibility
def get_transportation_accessibility_prompt(home_location: str, job_location: str) -> str:
    """
    Generate prompt for transportation accessibility analysis.

    Args:
        home_location: Where the individual lives
        job_location: Where the potential job/training is located

    Returns:
        Formatted prompt
    """
    return f"""
    Analyze transportation accessibility between these locations for a resident of an Environmental Justice community:

    Home Location: {home_location}
    Job/Training Location: {job_location}

    Provide:
    1. Public transportation options between these locations (routes, frequency, approximate travel time)
    2. Estimated costs for different transportation methods
    3. Potential transportation barriers and solutions
    4. Resources or programs that might help with transportation costs or access
    5. Alternative work/training arrangements if transportation is a significant barrier

    ONLY recommend resources and programs from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on practical, realistic solutions that acknowledge transportation challenges while providing actionable options.
    """

# Prompt for community-based training
def get_community_training_prompt(profile: Dict[str, Any]) -> str:
    """
    Generate prompt for community-based training recommendations.

    Args:
        profile: User profile information

    Returns:
        Formatted prompt
    """
    city = profile.get('location', 'Not specified')
    education_level = profile.get('education_level', 'Not specified')
    interests = ", ".join(profile.get('interests', ['Not specified']))

    return f"""
    Recommend community-based clean energy training programs for an individual with the following profile:

    Location: {city}
    Current Education Level: {education_level}
    Interests: {interests}

    Provide:
    1. Training programs located within or accessible to {city}
    2. Programs with minimal barriers to entry that match their current education level
    3. Support services that accompany the training (childcare, evening/weekend options, etc.)
    4. Funding opportunities or scholarships specifically for EJ community residents
    5. Success stories or pathways of others from similar backgrounds

    ONLY recommend programs and resources from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on programs with proven success in supporting EJ community members and addressing common barriers.
    """

# Prompt for multilingual resources
def get_multilingual_resources_prompt(language: str) -> str:
    """
    Generate prompt for multilingual clean energy resources.

    Args:
        language: Preferred language

    Returns:
        Formatted prompt
    """
    return f"""
    Identify clean energy resources and opportunities available in {language} for Massachusetts residents:

    Preferred Language: {language}

    Provide:
    1. Training programs or resources available in {language}
    2. Community organizations that offer services in {language}
    3. Translation or interpretation services for clean energy job seekers
    4. Multilingual job opportunities in the clean energy sector
    5. Cultural support resources for speakers of {language}

    ONLY recommend resources and programs from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on resources that are fully accessible in {language} or have strong language support.
    """

# Prompt for addressing systemic barriers
SYSTEMIC_BARRIERS_PROMPT = """
Provide guidance on addressing systemic barriers to clean energy careers for Environmental Justice community members:

1. Educational barriers and alternative qualification pathways
2. Financial barriers and available support systems
3. Networking and social capital development strategies
4. Addressing potential discrimination or bias in hiring
5. Building long-term career resilience and advancement

ONLY recommend resources and programs from our ecosystem partners:
- TPS Energy (tps-energy.com)
- Urban League of Eastern Massachusetts (ulem.org)
- Headlamp (myheadlamp.com)
- African Bridge Network (africanbn.org)
- Franklin Cummings Tech (franklincummings.edu)
- MassHire Career Centers (mass.gov/masshire-career-centers)
- MassCEC (masscec.com)
- ACT (joinact.org)
- Greentown Labs (greentownlabs.com)

ALWAYS reference your sources of information.
Focus on strengths-based approaches while acknowledging real challenges.
Provide concrete, actionable strategies rather than general advice.
"""

# Prompt for community-based projects
def get_community_projects_prompt(community: str) -> str:
    """
    Generate prompt for community-based clean energy projects.

    Args:
        community: The specific community or neighborhood

    Returns:
        Formatted prompt
    """
    return f"""
    Identify community-based clean energy projects and opportunities in {community}:

    Community: {community}

    Provide:
    1. Existing clean energy projects within the community
    2. Opportunities for community members to participate in local clean energy initiatives
    3. Job or training opportunities connected to community-based projects
    4. Organizations leading clean energy work in this community
    5. Resources for community members interested in clean energy entrepreneurship

    ONLY recommend projects and organizations from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on initiatives that provide direct benefits to community members and create accessible pathways to participation.
    """

# Prompts for specific educational backgrounds

# Vocational school graduates prompt
def get_vocational_graduate_prompt(vocational_field: str, years_experience: int = 0) -> str:
    """
    Generate a prompt for vocational school graduates seeking clean energy careers.

    Args:
        vocational_field: The vocational field of study/training
        years_experience: Years of experience in the field

    Returns:
        A formatted prompt for vocational graduates
    """
    return f"""
    Please provide guidance for a vocational school graduate from an Environmental Justice community seeking clean energy career opportunities:

    Vocational Training: {vocational_field}
    Years of Experience: {years_experience}

    Provide:
    1. Clean energy roles that align well with their vocational training
    2. Additional certifications or training that would enhance their employability
    3. Entry points into the clean energy sector specific to vocational graduates
    4. Ecosystem partners that actively recruit vocational graduates
    5. Success stories of vocational graduates in clean energy (if available)

    ONLY recommend resources, programs, and companies from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on practical pathways that build on their existing vocational training.
    """

# Technical trades workers prompt
def get_technical_trades_prompt(trade: str, years_experience: int, certifications: Optional[List[str]] = None) -> str:
    """
    Generate a prompt for technical trades workers transitioning to clean energy.

    Args:
        trade: The specific trade (electrician, plumber, etc.)
        years_experience: Years of experience in the trade
        certifications: List of current certifications

    Returns:
        A formatted prompt for trades workers
    """
    cert_text = ", ".join(certifications) if certifications else "None specified"

    return f"""
    Please provide guidance for a {trade} with {years_experience} years of experience from an Environmental Justice community transitioning to the clean energy sector:

    Trade: {trade}
    Years of Experience: {years_experience}
    Current Certifications: {cert_text}

    Provide:
    1. Clean energy roles where their trade skills transfer directly
    2. Clean energy-specific certifications that complement their trade background
    3. Transition pathways with minimal disruption to employment
    4. Ecosystem partners that value and recruit experienced trades workers
    5. Potential salary comparisons between traditional trade work and clean energy roles

    ONLY recommend resources, programs, and companies from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on leveraging their existing expertise while identifying specific clean energy applications.
    """

# University students/graduates prompt
def get_university_prompt(degree: str, field: str, graduation_status: str) -> str:
    """
    Generate a prompt for university students or graduates entering clean energy.

    Args:
        degree: The degree type (Bachelor's, Master's, etc.)
        field: Field of study
        graduation_status: Current student or graduation year

    Returns:
        A formatted prompt for university students/graduates
    """
    return f"""
    Please provide guidance for a university {graduation_status} with a {degree} in {field} from an Environmental Justice community seeking clean energy opportunities:

    Degree: {degree} in {field}
    Status: {graduation_status}

    Provide:
    1. Entry-level clean energy roles aligned with their academic background
    2. Internship or fellowship opportunities specifically for EJ community members
    3. Research or project-based opportunities in the clean energy sector
    4. Ecosystem partners with university recruitment programs
    5. Professional development resources to complement their academic knowledge

    ONLY recommend resources, programs, and companies from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on bridging academic knowledge with practical industry experience.
    """

# Workforce reentry prompt
def get_workforce_reentry_prompt(previous_field: str, years_gap: int, transferable_skills: Optional[List[str]] = None) -> str:
    """
    Generate a prompt for individuals reentering the workforce.

    Args:
        previous_field: Previous career field
        years_gap: Years away from the workforce
        transferable_skills: List of transferable skills

    Returns:
        A formatted prompt for workforce reentry
    """
    skills_text = ", ".join(transferable_skills) if transferable_skills else "Not specified"

    return f"""
    Please provide guidance for someone from an Environmental Justice community reentering the workforce after {years_gap} years and seeking clean energy opportunities:

    Previous Field: {previous_field}
    Employment Gap: {years_gap} years
    Transferable Skills: {skills_text}

    Provide:
    1. Clean energy roles suitable for career changers
    2. Training programs designed for workforce reentry
    3. Strategies for addressing employment gaps in applications
    4. Ecosystem partners with returnship or reentry programs
    5. Success stories of career changers in clean energy (if available)

    ONLY recommend resources, programs, and companies from our ecosystem partners.
    ALWAYS reference your sources of information.
    Focus on confidence-building pathways that acknowledge and value previous experience.
    """

# Comprehensive guidance prompt
COMPREHENSIVE_EJ_GUIDANCE_PROMPT = """
Provide comprehensive guidance for an Environmental Justice community member entering the Massachusetts clean energy workforce:

1. Assessment of local clean energy opportunities
2. Transportation and accessibility solutions
3. Training programs with support services
4. Financial resources and support systems
5. Community-based networks and support
6. Career pathway development with advancement opportunities
7. Addressing potential barriers with practical solutions
8. Specific pathways based on educational background:
   - For vocational school graduates
   - For technical trades workers
   - For university students/graduates
   - For workforce reentry individuals

ONLY recommend resources, programs, and companies from our ecosystem partners:
- TPS Energy (tps-energy.com)
- Urban League of Eastern Massachusetts (ulem.org)
- Headlamp (myheadlamp.com)
- African Bridge Network (africanbn.org)
- Franklin Cummings Tech (franklincummings.edu)
- MassHire Career Centers (mass.gov/masshire-career-centers)
- MassCEC (masscec.com)
- ACT (joinact.org)
- Greentown Labs (greentownlabs.com)

ALWAYS reference your sources of information.
Focus on practical, actionable steps with a timeline and approximate costs where possible.
Emphasize pathways that have worked for other EJ community members in similar situations.
Ensure your guidance is inclusive of all educational and career backgrounds.
"""
