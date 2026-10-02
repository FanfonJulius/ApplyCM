import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Program(Base):
    __tablename__ = "programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    field_of_study = Column(String, index=True, nullable=False)
    degree_type = Column(String, nullable=True)
    tuition_fee = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    language_of_instruction = Column(String, nullable=True)
    delivery_mode = Column(String, nullable=True)
    admission_requirements = Column(Text, nullable=True)
    required_documents = Column(Text, nullable=True)
    application_deadline = Column(String, nullable=True)
    class_size = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    school = relationship("School", back_populates="programs")