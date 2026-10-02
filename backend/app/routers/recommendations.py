"""
FastAPI router for ApplyCM AI Career Recommender.
Provides questionnaire metadata and recommendation inference.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.recommendation import (
    QuestionnaireMetaResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "/questions",
    response_model=QuestionnaireMetaResponse,
    summary="Get Career Questionnaire Metadata",
    description="Returns the 12 Likert-scale questions, academic series options, and subject choices for the student questionnaire.",
)
def get_questionnaire():
    return RecommendationService.get_questionnaire_meta()


@router.post(
    "/",
    response_model=RecommendationResponse,
    summary="Generate AI Career and University Recommendations",
    description="Accepts student questionnaire answers, runs the trained RandomForest model, and matches programs within the student's budget.",
)
def create_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    try:
        return RecommendationService.recommend(request, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}",
        )
