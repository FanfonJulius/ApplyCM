import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

SUBMISSION_SENDING = "sending"
SUBMISSION_SENT = "sent"
SUBMISSION_FAILED = "failed"


class ApplicationSubmission(Base):
    """One emailed application-profile PDF from a student to a school.

    The unique (student, school) pair doubles as the lock that stops the same
    application being emailed twice when Submit is clicked concurrently.
    """

    __tablename__ = "application_submissions"
    __table_args__ = (
        UniqueConstraint("student_id", "school_id", name="uq_application_submissions_student_school"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=SUBMISSION_SENDING)
    recipient_email = Column(String(255), nullable=True)
    error = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
