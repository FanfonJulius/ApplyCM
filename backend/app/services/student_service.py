from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.schemas.student_profile import (
    StudentProfileCreate,
    StudentProfileUpdate,
    ApplicationSectionStatus,
    DashboardSummaryResponse,
)
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.models.favorite import Favorite
from app.models.application import Application
from app.models.program import Program
from app.models.document import Document

class StudentService:
    @staticmethod
    def get_profile(db: Session, student_id: UUID) -> StudentProfile:
        return db.query(StudentProfile).filter(StudentProfile.id == student_id).first()

    @staticmethod
    def get_profile_by_user_id(db: Session, user_id: UUID) -> StudentProfile:
        return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()

    @staticmethod
    def create_profile(db: Session, profile_in: StudentProfileCreate) -> StudentProfile:
        db_profile = StudentProfile(**profile_in.model_dump())
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def update_profile(db: Session, student_id: UUID, profile_in: StudentProfileUpdate) -> StudentProfile:
        db_profile = StudentService.get_profile(db, student_id)
        if db_profile:
            for key, val in profile_in.model_dump(exclude_unset=True).items():
                setattr(db_profile, key, val)
            db.commit()
            db.refresh(db_profile)
        return db_profile


    @staticmethod
    def save_section(db: Session, user_id: UUID, section: str, section_in: BaseModel) -> StudentProfile:
        """Write one application-profile wizard section for the given account.

        The profile row is created on first save, so the wizard sections can be
        filled in any order. Ownership comes from ``user_id`` (the token), never
        from the request body.
        """
        values = section_in.model_dump()
        if section == "profile":
            values["full_name"] = f"{values['first_name']} {values['last_name']}"

        profile = StudentService.get_profile_by_user_id(db, user_id)
        if profile is None:
            profile = StudentProfile(user_id=user_id, **values)
            db.add(profile)
            try:
                db.commit()
            except IntegrityError:
                # A concurrent first save for this account won the insert on
                # the unique user_id; fall through and update that row instead.
                db.rollback()
                profile = StudentService.get_profile_by_user_id(db, user_id)
                if profile is None:
                    raise
            else:
                db.refresh(profile)
                return profile

        for key, val in values.items():
            setattr(profile, key, val)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_or_create_profile(db: Session, user_id: UUID) -> StudentProfile:
        profile = StudentService.get_profile_by_user_id(db, user_id)
        if profile is None:
            user = db.query(User).filter(User.id == user_id).first()
            default_name = user.email.split("@")[0].capitalize() if user and user.email else "Student"
            profile = StudentProfile(user_id=user_id, full_name=default_name)
            db.add(profile)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                profile = StudentService.get_profile_by_user_id(db, user_id)
            else:
                db.refresh(profile)
        return profile

    @staticmethod
    def get_dashboard_summary(db: Session, user_id: UUID) -> DashboardSummaryResponse:
        profile = StudentService.get_or_create_profile(db, user_id)

        # 1. Derive first name from profile.full_name or profile.first_name
        first_name = ""
        if profile.first_name and profile.first_name.strip():
            first_name = profile.first_name.strip()
        elif profile.full_name and profile.full_name.strip():
            first_name = profile.full_name.strip().split()[0]
        else:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.email:
                first_name = user.email.split("@")[0].capitalize()
            else:
                first_name = "Student"

        # 2. My ApplyCM Application progress (5 sections)
        is_profile_complete = bool(
            (profile.first_name and profile.last_name) or
            (profile.full_name and profile.full_name.strip() and profile.full_name.strip().lower() != "student")
        )
        is_contact_complete = bool(profile.phone and profile.phone.strip())
        is_education_complete = bool(
            (profile.education_summary and profile.education_summary.strip()) or
            (profile.secondary_school and profile.secondary_school.strip())
        )
        is_activities_complete = bool(
            profile.activity_name and profile.activity_name.strip() and
            profile.activity_description and profile.activity_description.strip()
        )
        is_writing_complete = bool(profile.writing_sample and profile.writing_sample.strip())

        sections = [
            ApplicationSectionStatus(
                key="profile",
                label="Profile",
                href="/application/profile",
                complete=is_profile_complete,
            ),
            ApplicationSectionStatus(
                key="contact",
                label="Contact",
                href="/application/contact",
                complete=is_contact_complete,
            ),
            ApplicationSectionStatus(
                key="education",
                label="Education",
                href="/application/education",
                complete=is_education_complete,
            ),
            ApplicationSectionStatus(
                key="activities",
                label="Activities and experiences",
                href="/application/activities",
                complete=is_activities_complete,
            ),
            ApplicationSectionStatus(
                key="writing",
                label="Writing",
                href="/application/writing",
                complete=is_writing_complete,
            ),
        ]

        completed_count = sum(1 for s in sections if s.complete)
        overall_progress = int(round((completed_count / len(sections)) * 100))

        # 3. My Universities counts
        favorited_universities = db.query(Favorite).filter(Favorite.student_id == profile.id).count()

        universities_in_progress = (
            db.query(Application)
            .filter(Application.student_id == profile.id, Application.status != "submitted")
            .count()
        )

        fav_school_ids = {
            f.school_id for f in db.query(Favorite.school_id).filter(Favorite.student_id == profile.id).all()
        }
        app_school_ids = {
            p.school_id
            for p in db.query(Program.school_id)
            .join(Application, Application.program_id == Program.id)
            .filter(Application.student_id == profile.id)
            .all()
        }
        universities_on_list = len(fav_school_ids.union(app_school_ids))

        # 4. Outstanding documents
        uploaded_docs = db.query(Document).filter(Document.student_id == profile.id).count()
        required_docs_outstanding = max(0, 2 - uploaded_docs) if uploaded_docs < 2 else 0

        return DashboardSummaryResponse(
            firstName=first_name,
            first_name=first_name,
            applicationSections=sections,
            application_sections=sections,
            overallProgress=overall_progress,
            overall_progress=overall_progress,
            universitiesOnList=universities_on_list,
            universities_on_list=universities_on_list,
            universitiesInProgress=universities_in_progress,
            universities_in_progress=universities_in_progress,
            favoritedUniversities=favorited_universities,
            favorited_universities=favorited_universities,
            requiredDocumentsOutstanding=required_docs_outstanding,
            required_documents_outstanding=required_docs_outstanding,
        )

