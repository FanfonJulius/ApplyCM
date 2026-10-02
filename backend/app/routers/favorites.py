from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.favorite import FavoriteCreateRequest, FavoriteSchoolItem
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("", response_model=List[FavoriteSchoolItem])
@router.get("/", response_model=List[FavoriteSchoolItem], include_in_schema=False)
def list_my_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns list of schools favorited by the logged-in student (derived from JWT token).
    """
    return FavoriteService.get_student_favorites(db, user_id=current_user.id)

@router.post("", response_model=FavoriteSchoolItem, status_code=status.HTTP_200_OK)
@router.post("/", response_model=FavoriteSchoolItem, status_code=status.HTTP_200_OK, include_in_schema=False)
def add_favorite(
    body: FavoriteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adds a school to the current student's favorites (idempotent).
    """
    return FavoriteService.add_favorite(db, user_id=current_user.id, school_id=body.school_id)

@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    school_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Removes a school from the current student's favorites.
    """
    FavoriteService.remove_favorite(db, user_id=current_user.id, school_id=school_id)
    return None
