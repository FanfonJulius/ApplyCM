from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ProgramBase(BaseModel):
    field_of_study: str
    degree_type: Optional[str] = None
    tuition_fee: Optional[str] = None
    duration: Optional[str] = None
    language_of_instruction: Optional[str] = None
    delivery_mode: Optional[str] = None
    admission_requirements: Optional[str] = None
    required_documents: Optional[str] = None
    application_deadline: Optional[str] = None
    class_size: Optional[int] = None
    description: Optional[str] = None

class ProgramCreate(ProgramBase):
    school_id: UUID

class ProgramUpdate(BaseModel):
    field_of_study: Optional[str] = None
    degree_type: Optional[str] = None
    tuition_fee: Optional[str] = None
    duration: Optional[str] = None
    language_of_instruction: Optional[str] = None
    delivery_mode: Optional[str] = None
    admission_requirements: Optional[str] = None
    required_documents: Optional[str] = None
    application_deadline: Optional[str] = None
    class_size: Optional[int] = None
    description: Optional[str] = None

class Program(ProgramBase):
    id: UUID
    school_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True