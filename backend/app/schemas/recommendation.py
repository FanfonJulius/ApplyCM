"""
Pydantic schemas for ApplyCM AI Career Recommender.
"""

from uuid import UUID
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    id: str
    statement: str
    category: Optional[str] = None
    min_value: int = 1
    max_value: int = 5


class QuestionnaireMetaResponse(BaseModel):
    questions: List[QuestionItem]
    series_options: List[str]
    subject_options: List[str]
    default_budget: float = 600000.0
    currency: str = "FCFA"


class RecommendationRequest(BaseModel):
    series: str = Field(..., description="Academic series, e.g. Science, Arts, Commercial, Technical")
    subjects: List[str] = Field(..., min_length=1, max_length=3, description="Up to 3 strongest subjects")
    answers: Dict[str, int] = Field(..., description="Ratings 1-5 for q1_building to q12_writing_reading")
    max_budget: Optional[float] = Field(None, description="Maximum yearly tuition budget in FCFA")


class MatchedProgram(BaseModel):
    id: str
    program_title: str
    school_id: str
    school_name: str
    school_location: Optional[str] = None
    school_website: Optional[str] = None
    school_logo: Optional[str] = None
    degree_type: Optional[str] = None
    tuition_fee: Optional[str] = None
    parsed_tuition: Optional[float] = None
    duration: Optional[str] = None
    admission_requirements: Optional[str] = None
    description: Optional[str] = None
    matched_target_field: str
    is_within_budget: bool
    budget_fit_score: float = 1.0


class RecommendedField(BaseModel):
    field_name: str
    rank: int
    probability: float
    percentage: float
    description: str
    explanation: str
    programs_available_count: int
    programs: List[MatchedProgram]


class RecommendationResponse(BaseModel):
    student_summary: Dict[str, Any]
    top_fields: List[RecommendedField]
    all_matching_programs: List[MatchedProgram]
    total_matching_programs: int
    model_info: Dict[str, Any]
