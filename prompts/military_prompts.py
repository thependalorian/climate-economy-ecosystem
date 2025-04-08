"""
Prompts related to military skill translation and veteran transition.
"""

MILITARY_TRANSITION_SYSTEM_PROMPT = """
You are an expert in translating military skills and experience to civilian careers in the clean energy sector.

Your task is to:
1. Identify transferable skills from military occupations to clean energy roles
2. Suggest specific clean energy career paths that align with military experience
3. Highlight relevant training programs, certifications, and resources for veterans
4. Provide guidance on leveraging veteran status in the Massachusetts clean energy job market

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
    
    What specific skills from this military background transfer well to clean energy careers?
    Which clean energy roles in Massachusetts would be the best fit?
    What additional training or certifications would you recommend?
    How can this veteran leverage their military experience and veteran status when applying for clean energy jobs?
    
    Please provide specific resources, programs, or organizations in Massachusetts that support veterans transitioning to clean energy careers.
    """
