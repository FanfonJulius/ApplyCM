from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.favorite import Favorite
from app.models.school import School
from app.models.student_profile import StudentProfile

class FavoriteService:
    @staticmethod
    def get_or_create_student_profile(db: Session, user_id: UUID) -> StudentProfile:
        """Finds or creates a student profile linked to the user account."""
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if not profile:
            profile = StudentProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def get_student_favorites(db: Session, user_id: UUID) -> List[School]:
        """Returns the list of schools favorited by the student derived from the user token."""
        profile = FavoriteService.get_or_create_student_profile(db, user_id)
        return (
            db.query(School)
            .join(Favorite, Favorite.school_id == School.id)
            .filter(Favorite.student_id == profile.id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    @staticmethod
    def add_favorite(db: Session, user_id: UUID, school_id: UUID) -> School:
        """Creates a favorite link between current student and the school. Idempotent."""
        profile = FavoriteService.get_or_create_student_profile(db, user_id)

        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")

        existing = db.query(Favorite).filter(
            Favorite.student_id == profile.id,
            Favorite.school_id == school_id
        ).first()

        if not existing:
            fav = Favorite(student_id=profile.id, school_id=school_id)
            db.add(fav)
            db.commit()

        return school

    @staticmethod
    def remove_favorite(db: Session, user_id: UUID, school_id: UUID) -> bool:
        """Removes the favorite link between current student and the school."""
        profile = FavoriteService.get_or_create_student_profile(db, user_id)
        fav = db.query(Favorite).filter(
            Favorite.student_id == profile.id,
            Favorite.school_id == school_id
        ).first()
        if fav:
            db.delete(fav)
            db.commit()
            return True
        return False
