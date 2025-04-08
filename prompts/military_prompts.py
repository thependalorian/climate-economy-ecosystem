"""
Prompts related to military skill translation and veteran transition.
"""

MILITARY_TRANSITION_SYSTEM_PROMPT = """
You are Marcus, an expert in translating military skills and experience to civilian careers in the clean energy sector.

Background: You are a Marine Corps veteran with 8 years of service who successfully transitioned to the clean energy sector 5 years ago. You now help other veterans find meaningful careers in clean energy. You have deep knowledge of military occupational specialties across all branches and understand how military skills transfer to civilian clean energy roles.

Personality: You are direct, motivating, and detail-oriented. You speak with authority and clarity while remaining approachable. You understand the challenges of military transition and provide straightforward guidance with empathy. You use military analogies when helpful but avoid unnecessary jargon when speaking to civilians.

Your task is to:
1. Identify transferable skills from military occupations to clean energy roles
2. Suggest specific clean energy career paths that align with military experience
3. Highlight relevant training programs, certifications, and resources for veterans
4. Provide guidance on leveraging veteran status in the Massachusetts clean energy job market

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

Focus on providing practical, actionable advice that helps veterans translate their military experience into valuable assets for the clean energy workforce.
"""

def get_skill_translation_prompt(mos: str, branch: str, years_experience: int) -> str:
    """
    Generate a prompt for translating military skills to civilian clean energy careers.

    Args:
        mos: Military Occupational Specialty code or title
        branch: Branch of military service
        years_experience: Years of military service

    Returns:
        A formatted prompt for military skill translation
    """
    return f"""
    Please analyze the following military background for clean energy career opportunities:

    MOS/Military Role: {mos}
    Branch of Service: {branch}
    Years of Service: {years_experience}

    Provide:
    1. Specific skills from this military background that transfer well to clean energy careers
    2. 3-5 clean energy roles in Massachusetts that would be the best fit based on their military experience
    3. Additional training or certifications that would enhance their transition (with timeline and cost estimates)
    4. Strategies for leveraging military experience and veteran status when applying for clean energy jobs
    5. Specific ecosystem partners that actively recruit and support veterans

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
    Focus on practical, actionable advice with specific examples of success stories when possible.
    """

# Prompt for veteran education benefits
def get_veteran_education_prompt(gi_bill_eligible: bool, post_911: bool = False) -> str:
    """
    Generate a prompt for veteran education benefits for clean energy training.

    Args:
        gi_bill_eligible: Whether the veteran is eligible for GI Bill benefits
        post_911: Whether the veteran is eligible for Post-9/11 GI Bill

    Returns:
        A formatted prompt for veteran education benefits
    """
    gi_bill_type = "Post-9/11 GI Bill" if post_911 else "Montgomery GI Bill"
    eligibility_text = f"Eligible for {gi_bill_type}" if gi_bill_eligible else "Not eligible for GI Bill benefits"

    return f"""
    Please provide guidance on educational pathways for a veteran transitioning to the clean energy sector:

    Education Benefit Status: {eligibility_text}

    Provide:
    1. Clean energy training programs in Massachusetts that accept GI Bill benefits
    2. Alternative funding sources for veterans without GI Bill eligibility
    3. Accelerated training options that leverage military experience
    4. Certification programs with the highest return on investment
    5. Ecosystem partners with specific veteran education initiatives

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
    Focus on maximizing veteran benefits while minimizing out-of-pocket costs.
    """

# Prompt for veteran entrepreneurship
def get_veteran_entrepreneurship_prompt(business_idea: str, startup_phase: str) -> str:
    """
    Generate a prompt for veteran entrepreneurship in clean energy.

    Args:
        business_idea: Brief description of the business idea
        startup_phase: Current phase of the startup (idea, planning, launch, etc.)

    Returns:
        A formatted prompt for veteran entrepreneurship
    """
    return f"""
    Please provide guidance for a veteran entrepreneur in the clean energy sector:

    Business Idea: {business_idea}
    Current Phase: {startup_phase}

    Provide:
    1. Resources specifically for veteran entrepreneurs in clean energy
    2. Funding opportunities targeted at veteran-owned clean energy businesses
    3. Incubator or accelerator programs that prioritize veteran entrepreneurs
    4. Networking opportunities within the Massachusetts clean energy ecosystem
    5. Success stories of veteran-owned clean energy businesses (if available)

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
    Focus on leveraging veteran status as a business advantage while providing practical startup guidance.
    """

# Prompt for veteran resume translation
def get_resume_translation_prompt(military_role: str, target_sector: str) -> str:
    """
    Generate a prompt for translating military resume to clean energy applications.

    Args:
        military_role: Military role or MOS
        target_sector: Target clean energy sector

    Returns:
        A formatted prompt for resume translation
    """
    return f"""
    Please provide guidance on translating military experience to a clean energy resume:

    Military Role: {military_role}
    Target Clean Energy Sector: {target_sector}

    Provide:
    1. Key military terms and their civilian clean energy equivalents
    2. Skills to emphasize for {target_sector} positions
    3. Accomplishments to highlight and how to quantify them
    4. Resume format recommendations for clean energy employers
    5. Before/after examples of military descriptions translated to clean energy terminology

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
    Focus on translating military achievements into terms that resonate with clean energy employers.
    """

# Comprehensive veteran guidance prompt
COMPREHENSIVE_VETERAN_GUIDANCE_PROMPT = """
Provide comprehensive guidance for a veteran transitioning to the Massachusetts clean energy workforce:

1. Skill translation and career matching
2. Education and training pathways with veteran benefits
3. Job search strategies specific to veterans
4. Networking in the clean energy sector
5. Leveraging veteran status in applications and interviews
6. Entrepreneurship opportunities in clean energy
7. Support systems and resources for the transition process

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
Emphasize pathways that have worked for other veterans in similar situations.
"""
