from typing import Dict, List, Optional, Any, TypedDict, Union
from pydantic import BaseModel

class ClimateState(TypedDict):
    """State for climate assistant workflow"""
    user_query: str
    user_id: str
    context: List[Dict[str, Any]]
    retrieved_memories: List[Dict[str, Any]]
    report_insights: List[Dict[str, Any]]
    job_recommendations: List[Dict[str, Any]]
    training_paths: List[Dict[str, Any]]
    response: Optional[str]
    error: Optional[str]
    resume_text: Optional[str]
    resume_analysis: Optional[Dict[str, Any]]
    stream_tokens: Optional[bool]
    socket_id: Optional[str]
    is_ej_community: Optional[bool]
    is_veteran: Optional[bool]
    military_data: Optional[Dict[str, Any]]
    metrics: Dict[str, Any]

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
    
class TrainingProgramConfig(BaseModel):
    """Configuration for training program recommendations"""
    user_id: str
    location_preference: Optional[str] = None
    skills_to_develop: List[str] = []
    current_skills: List[str] = []
    budget_constraint: Optional[str] = None
    is_ej_community: bool = False
    needs_funding_assistance: bool = False 