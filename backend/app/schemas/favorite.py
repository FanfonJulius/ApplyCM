from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class FavoriteCreateRequest(BaseModel):
    school_id: UUID

class FavoriteSchoolItem(BaseModel):
    id: UUID
    name: str
    location: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    contact_email: Optional[str] = None
    application_deadline: Optional[str] = None
    rolling_admission: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FavoriteResponse(BaseModel):
    id: UUID
    student_id: UUID
    school_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
