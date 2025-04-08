from typing import Dict, List, Optional, Any, TypedDict
from pydantic import BaseModel

class ClimateState(TypedDict):
    """
    State for climate assistant workflow

    This state tracks all information related to user interactions,
    including context, recommendations, and user-specific data.
    """
    # Core fields
    user_query: str
    user_id: str
    chat_id: Optional[str]
    message_id: Optional[str]

    # Context and memory
    context: List[Dict[str, Any]]
    retrieved_memories: List[Dict[str, Any]]

    # Results and recommendations
    report_insights: List[Dict[str, Any]]
    job_recommendations: List[Dict[str, Any]]
    training_paths: List[Dict[str, Any]]
    response: Optional[str]
    error: Optional[str]

    # User profile data
    resume_text: Optional[str]
    resume_analysis: Optional[Dict[str, Any]]

    # Technical fields
    stream_tokens: Optional[bool]
    socket_id: Optional[str]
    metrics: Dict[str, Any]

    # User type flags
    is_ej_community: Optional[bool]
    is_veteran: Optional[bool]

    # RLHF-related fields
    reasoning_steps: Optional[List[Dict[str, Any]]]
    feedback_data: Optional[Dict[str, Any]]
    satisfaction_score: Optional[float]

    # Military-specific fields
    military_data: Optional[Dict[str, Any]]

    # EJ communities fields
    ej_geospatial_data: Optional[Dict[str, Any]]
    transportation_analysis: Optional[Dict[str, Any]]
    community_projects: Optional[List[Dict[str, Any]]]
    preferred_language: Optional[str]
    cultural_context: Optional[str]
    gateway_city_data: Optional[Dict[str, Any]]

    # International professionals fields
    international_credentials: Optional[Dict[str, Any]]
    credential_evaluation: Optional[Dict[str, Any]]
    regulatory_roadmap: Optional[Dict[str, Any]]
    experience_translation: Optional[Dict[str, Any]]
    cultural_integration_guide: Optional[Dict[str, Any]]
    origin_country: Optional[str]
    international_education: Optional[Dict[str, Any]]

    # Configuration fields
    job_config: Optional[Dict[str, Any]]

class SearchConfig(BaseModel):
    """Configuration for search operations"""
    query: str
    user_id: str
    limit: int = 5
    categories: List[str] = []
    threshold: float = 0.5
    include_web_search: bool = False

class MemoryResult(BaseModel):
    """Result from memory search"""
    id: str
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    category: str

class ResumeAnalysisConfig(BaseModel):
    """Configuration for resume analysis"""
    user_id: str
    resume_text: str
    extract_skills: bool = True
    extract_education: bool = True
    extract_experience: bool = True
    assess_climate_relevance: bool = True
    translate_military_skills: bool = False
    evaluate_international_credentials: bool = False
    origin_country: Optional[str] = None
    target_field: Optional[str] = None

class JobRecommendationConfig(BaseModel):
    """Configuration for job recommendations"""
    user_id: str
    location_preference: Optional[str] = None
    remote_preference: Optional[bool] = None
    sectors: List[str] = []
    skills: List[str] = []
    experience_level: Optional[str] = None
    is_veteran: bool = False
    has_international_credentials: bool = False
    is_ej_community: bool = False
    preferred_language: Optional[str] = None
    origin_country: Optional[str] = None
    transportation_constraints: Optional[Dict[str, Any]] = None

class TrainingProgramConfig(BaseModel):
    """Configuration for training program recommendations"""
    user_id: str
    location_preference: Optional[str] = None
    skills_to_develop: List[str] = []
    current_skills: List[str] = []
    budget_constraint: Optional[str] = None
    is_ej_community: bool = False
    needs_funding_assistance: bool = False
    preferred_language: Optional[str] = None
    has_transportation_constraints: bool = False
    has_childcare_needs: bool = False
    has_international_credentials: bool = False

class FeedbackConfig(BaseModel):
    """Configuration for user feedback collection"""
    user_id: str
    chat_id: str
    message_id: Optional[str] = None
    step_id: Optional[str] = None
    feedback_type: str  # 'positive', 'negative', etc.
    feedback_score: Optional[int] = None  # 1-5 scale
    feedback_details: Optional[str] = None

class EJCommunityConfig(BaseModel):
    """Configuration for EJ community analysis"""
    user_id: str
    location: str
    preferred_language: Optional[str] = None
    transportation_constraints: Optional[Dict[str, Any]] = None
    childcare_needs: Optional[bool] = None
    cultural_context: Optional[str] = None
    community_interests: Optional[List[str]] = None

class InternationalProfessionalConfig(BaseModel):
    """Configuration for international professional support"""
    user_id: str
    origin_country: str
    credentials: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    target_field: Optional[str] = None
    language_proficiency: Optional[Dict[str, Any]] = None
    years_in_massachusetts: Optional[int] = None