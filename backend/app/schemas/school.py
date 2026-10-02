from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class SchoolBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    contact_email: Optional[str] = None
    application_deadline: Optional[str] = None
    rolling_admission: Optional[bool] = False

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    contact_email: Optional[str] = None
    application_deadline: Optional[str] = None
    rolling_admission: Optional[bool] = None

class School(SchoolBase):
    id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True