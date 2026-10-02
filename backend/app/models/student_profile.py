import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    # Derived from first_name + last_name when the "profile" section is saved;
    # nullable so a student can save any wizard section first.
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    education_summary = Column(Text, nullable=True)
    writing_sample = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Section: profile (personal details)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    declared_state = Column(String(100), nullable=True)

    # Section: contact
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(32), nullable=True)

    # Section: education
    secondary_school = Column(String(255), nullable=True)
    o_level_slip_url = Column(Text, nullable=True)
    a_level_slip_url = Column(Text, nullable=True)

    # Section: testing
    o_level_passes = Column(String(255), nullable=True)
    a_level_points = Column(String(255), nullable=True)
    english_test_type = Column(String(50), nullable=True)
    english_test_score = Column(String(100), nullable=True)

    # Section: activities
    activity_name = Column(String(200), nullable=True)
    activity_role = Column(String(200), nullable=True)
    activity_description = Column(Text, nullable=True)
    honors_awards = Column(Text, nullable=True)

    # Section: writing (writing_sample holds the personal statement)
    essay_prompt = Column(String(100), nullable=True)
    additional_info = Column(Text, nullable=True)
