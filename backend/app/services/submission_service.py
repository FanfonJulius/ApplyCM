"""Submits a student's application profile (as a PDF) to chosen favorite schools."""

import logging
from datetime import datetime, timedelta, timezone
from html import escape
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.application_submission import (
    SUBMISSION_FAILED,
    SUBMISSION_SENDING,
    SUBMISSION_SENT,
    ApplicationSubmission,
)
from app.models.favorite import Favorite
from app.models.school import School
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.student_profile import StudentProfile as StudentProfileSchema
from app.schemas.submission import SubmissionCreateResponse, SubmissionItem, SubmissionResult
from app.services.email_service import (
    Attachment,
    EmailMessage,
    EmailNotConfiguredError,
    EmailSendError,
    ensure_email_configured,
    send_email,
)
from app.services.pdf_service import application_pdf_filename, build_application_pdf
from app.services.student_service import StudentService

logger = logging.getLogger(__name__)

# The five sections shown in the wizard sidebar; "testing" is optional.
REQUIRED_SECTIONS: Dict[str, str] = {
    "profile": "Profile",
    "contact": "Contact",
    "education": "Education",
    "activities": "Activities and experiences",
    "writing": "Writing",
}
# A "sending" row this old belongs to a request that died mid-send; allow a retry.
STALE_SENDING_AFTER = timedelta(minutes=15)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _applicant_name(profile: StudentProfile) -> str:
    name = " ".join(p.strip() for p in (profile.first_name, profile.last_name) if p and p.strip())
    return name or (profile.full_name or "").strip() or "A student"


class SubmissionService:
    @staticmethod
    def missing_sections(profile: Optional[StudentProfile]) -> List[str]:
        if profile is None:
            return list(REQUIRED_SECTIONS)
        completed = set(StudentProfileSchema.model_validate(profile).completed_sections)
        return [key for key in REQUIRED_SECTIONS if key not in completed]

    @staticmethod
    def get_complete_profile(db: Session, user_id: UUID) -> StudentProfile:
        profile = StudentService.get_profile_by_user_id(db, user_id)
        missing = SubmissionService.missing_sections(profile)
        if missing:
            labels = ", ".join(REQUIRED_SECTIONS[key] for key in missing)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Complete these sections of your application before submitting: {labels}.",
            )
        return profile

    @staticmethod
    def list_submissions(db: Session, user_id: UUID) -> List[SubmissionItem]:
        profile = StudentService.get_profile_by_user_id(db, user_id)
        if profile is None:
            return []
        rows = (
            db.query(ApplicationSubmission, School.name)
            .join(School, School.id == ApplicationSubmission.school_id)
            .filter(ApplicationSubmission.student_id == profile.id)
            .order_by(ApplicationSubmission.created_at.desc())
            .all()
        )
        return [
            SubmissionItem(
                school_id=row.school_id,
                school_name=name,
                status=row.status,
                recipient_email=row.recipient_email,
                error=row.error,
                sent_at=row.sent_at,
                updated_at=row.updated_at,
            )
            for row, name in rows
        ]

    @staticmethod
    def submit(db: Session, user: User, school_ids: List[UUID]) -> SubmissionCreateResponse:
        try:
            ensure_email_configured()
        except EmailNotConfiguredError as exc:
            logger.error("Application submit refused: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sending applications is temporarily unavailable. Please try again later.",
            ) from exc

        profile = SubmissionService.get_complete_profile(db, user.id)
        ids = list(dict.fromkeys(school_ids))
        schools = {
            school.id: school
            for school in db.query(School)
            .join(Favorite, Favorite.school_id == School.id)
            .filter(Favorite.student_id == profile.id, School.id.in_(ids))
            .all()
        }
        if len(schools) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only submit your application to universities in your list.",
            )

        pdf = Attachment(filename=application_pdf_filename(profile), content=build_application_pdf(profile))
        student_email = profile.email or user.email
        results: List[SubmissionResult] = []
        sent_names: List[str] = []

        for school_id in ids:
            school = schools[school_id]
            skipped = SubmissionService._claim(db, profile.id, school)
            if skipped:
                results.append(SubmissionResult(school_id=school.id, school_name=school.name, status=skipped))
                continue

            error = SubmissionService._send_to_school(profile, school, pdf, reply_to=student_email)
            SubmissionService._finish(db, profile.id, school.id, error)
            if error is None:
                sent_names.append(school.name)
            results.append(SubmissionResult(
                school_id=school.id,
                school_name=school.name,
                status="failed" if error else "sent",
                error=error,
            ))

        student_copy_sent = False
        if sent_names:
            student_copy_sent = SubmissionService._send_student_copy(profile, user, sent_names, pdf)

        return SubmissionCreateResponse(
            results=results,
            sent_count=len(sent_names),
            student_copy_sent=student_copy_sent,
        )

    # --- internals -------------------------------------------------------

    @staticmethod
    def _claim(db: Session, student_id: UUID, school: School) -> Optional[str]:
        """Marks (student, school) as "sending". Returns None when this request
        now owns the send, otherwise the reason it must be skipped."""
        now = _now()
        row = (
            db.query(ApplicationSubmission)
            .filter(ApplicationSubmission.student_id == student_id, ApplicationSubmission.school_id == school.id)
            .first()
        )
        if row is None:
            db.add(ApplicationSubmission(
                student_id=student_id,
                school_id=school.id,
                status=SUBMISSION_SENDING,
                recipient_email=school.contact_email,
                created_at=now,
                updated_at=now,
            ))
            try:
                db.commit()
                return None
            except IntegrityError:
                db.rollback()
                return "in_progress"

        if row.status == SUBMISSION_SENT:
            return "already_sent"

        claimed = db.execute(
            update(ApplicationSubmission)
            .where(
                ApplicationSubmission.id == row.id,
                or_(
                    ApplicationSubmission.status == SUBMISSION_FAILED,
                    and_(
                        ApplicationSubmission.status == SUBMISSION_SENDING,
                        ApplicationSubmission.updated_at < now - STALE_SENDING_AFTER,
                    ),
                ),
            )
            .values(status=SUBMISSION_SENDING, error=None, recipient_email=school.contact_email, updated_at=now)
            .execution_options(synchronize_session=False)
        ).rowcount
        db.commit()
        if claimed == 1:
            return None
        db.refresh(row)
        return "already_sent" if row.status == SUBMISSION_SENT else "in_progress"

    @staticmethod
    def _finish(db: Session, student_id: UUID, school_id: UUID, error: Optional[str]) -> None:
        now = _now()
        db.execute(
            update(ApplicationSubmission)
            .where(ApplicationSubmission.student_id == student_id, ApplicationSubmission.school_id == school_id)
            .values(
                status=SUBMISSION_FAILED if error else SUBMISSION_SENT,
                error=error,
                sent_at=None if error else now,
                updated_at=now,
            )
            .execution_options(synchronize_session=False)
        )
        db.commit()

    @staticmethod
    def _send_to_school(profile: StudentProfile, school: School, pdf: Attachment, reply_to: Optional[str]) -> Optional[str]:
        if not school.contact_email:
            return "This university has no admissions email on file yet."

        name = _applicant_name(profile)
        subject = f"Application from {name} via ApplyCM"
        contact = ", ".join(v for v in (profile.email, profile.phone) if v)
        text = (
            f"Dear {school.name} Admissions Office,\n\n"
            f"{name} has submitted their application profile to {school.name} through ApplyCM.\n"
            f"The complete profile is attached as a PDF ({pdf.filename}).\n\n"
            f"To contact the applicant, reply to this email or use: {contact}.\n\n"
            "ApplyCM - one profile, many Cameroonian universities."
        )
        html = (
            f"<p>Dear {escape(school.name)} Admissions Office,</p>"
            f"<p><strong>{escape(name)}</strong> has submitted their application profile to "
            f"{escape(school.name)} through ApplyCM. The complete profile is attached as a PDF "
            f"(<em>{escape(pdf.filename)}</em>).</p>"
            f"<p>To contact the applicant, reply to this email or use: {escape(contact)}.</p>"
            "<p style=\"color:#64748b\">ApplyCM - one profile, many Cameroonian universities.</p>"
        )
        try:
            send_email(EmailMessage(
                to=[school.contact_email],
                subject=subject,
                html=html,
                text=text,
                reply_to=reply_to,
                attachments=[pdf],
            ))
        except (EmailSendError, EmailNotConfiguredError) as exc:
            logger.warning("Application email to school %s failed: %s", school.id, exc)
            return str(exc)
        except Exception:
            logger.exception("Unexpected error emailing school %s", school.id)
            return "Unexpected error while sending. Please try again."
        return None

    @staticmethod
    def _send_student_copy(profile: StudentProfile, user: User, school_names: List[str], pdf: Attachment) -> bool:
        recipients = list(dict.fromkeys(e.strip().lower() for e in (user.email, profile.email) if e and e.strip()))
        name = _applicant_name(profile)
        count = len(school_names)
        subject = f"Your ApplyCM application was sent to {count} {'university' if count == 1 else 'universities'}"
        text = (
            f"Hi {name},\n\nYour application profile was emailed to:\n"
            + "".join(f"- {n}\n" for n in school_names)
            + "\nA copy of the PDF they received is attached. Universities will reply to you directly.\n\nApplyCM"
        )
        html = (
            f"<p>Hi {escape(name)},</p><p>Your application profile was emailed to:</p><ul>"
            + "".join(f"<li>{escape(n)}</li>" for n in school_names)
            + "</ul><p>A copy of the PDF they received is attached. "
            "Universities will reply to you directly.</p><p>ApplyCM</p>"
        )
        try:
            send_email(EmailMessage(to=recipients, subject=subject, html=html, text=text, attachments=[pdf]))
        except Exception:
            logger.exception("Could not send the student copy for profile %s", profile.id)
            return False
        return True
