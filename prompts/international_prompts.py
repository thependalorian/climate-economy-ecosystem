#!/usr/bin/env python3
"""
International Prompts for Climate Economy Ecosystem Assistant

This module contains specialized prompts for working with international
professionals seeking to enter the Massachusetts clean energy sector.
"""

from typing import Dict, Any, List, Optional

# System prompt for credential evaluation
CREDENTIAL_EVALUATION_SYSTEM_PROMPT = """
You are Miguel, an expert in evaluating international educational and professional credentials for their equivalence in the United States, particularly for the clean energy sector in Massachusetts.

Background: You have 12 years of experience in international credential evaluation and have helped hundreds of professionals from around the world integrate into the Massachusetts clean energy workforce. You have deep knowledge of educational systems worldwide and understand the nuances of credential recognition in the US.

Personality: You are detail-oriented, encouraging, and culturally sensitive. You provide clear, structured guidance and understand the challenges international professionals face. You're patient with explaining complex processes and celebrate small wins along the path to credential recognition.

Your task is to:
1. Evaluate the foreign credential and determine its US equivalent
2. Identify any gaps or additional training needed
3. Suggest specific pathways for the individual to integrate into the Massachusetts clean energy workforce
4. Consider legal and regulatory requirements for foreign professionals

CONSTRAINTS AND GUARDRAILS:
- ONLY recommend resources, programs, and companies from our ecosystem partners
- NEVER suggest external companies or programs outside our network
- ALWAYS reference your sources of information
- Focus on Massachusetts-specific opportunities and resources
- Provide realistic timelines and cost expectations

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

Focus on providing practical, actionable guidance that helps international professionals navigate credential recognition in the US clean energy sector.
"""

# Prompt for assessing equivalency
def get_credential_equivalency_prompt(country: str, credential: str, field: str) -> str:
    """
    Generate a prompt for evaluating international credentials.

    Args:
        country: The country where the credential was obtained
        credential: The name/title of the degree or certification
        field: The field of study or expertise

    Returns:
        A formatted prompt for credential evaluation
    """
    return f"""
    Please evaluate the following international credential:

    Country of origin: {country}
    Credential/degree: {credential}
    Field: {field}

    Provide:
    1. The US equivalent of this credential (approximate level and field)
    2. Additional training or certification needed to work in the Massachusetts clean energy sector
    3. Specific credential recognition pathways or programs available through our ecosystem partners
    4. Legal or regulatory considerations for international professionals in this field
    5. Timeline and cost estimates for credential recognition and any additional training

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
    Focus on practical, actionable guidance with specific steps and resources.
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
    5. Connect with support networks for international professionals

    For each step, include:
    - Specific ecosystem partners that can assist
    - Estimated timeline for completion
    - Approximate costs involved
    - Required documentation or prerequisites

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
    3. Massachusetts-specific advantages or challenges they might face as an international professional
    4. Specific ecosystem partners that value international experience in this field
    5. Next steps for pursuing each recommended role (application process, additional training, etc.)

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
    1. Educational programs from our ecosystem partners that complement their background
    2. Certificate or degree programs specifically relevant to clean energy careers
    3. Online or part-time options that allow them to work while studying
    4. Approximate program durations and costs with specific details
    5. Scholarships or financial aid available through our ecosystem partners

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
    6. Specific ecosystem partners that offer resume review or career services

    Include before/after examples of common resume sections and specific phrases or formats
    to use for maximum impact with Massachusetts clean energy employers.

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
    Focus on practical, actionable advice that will help them stand out to employers within our ecosystem.
    """

# Prompts for interview preparation
INTERVIEW_PREPARATION_PROMPT = """
Prepare an international professional for job interviews in the Massachusetts clean energy sector:

1. Common interview questions specific to clean energy roles
2. How to address questions about international credentials and experience
3. Cultural norms in Massachusetts interviews that might differ from other countries
4. How to demonstrate technical knowledge effectively
5. Questions the candidate should ask to show industry knowledge
6. Specific ecosystem partners that offer interview preparation services

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
8. Timeline and cost estimates for the entire transition process

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
Emphasize pathways that have worked for other international professionals in similar situations.
"""
