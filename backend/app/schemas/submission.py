from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

MAX_SCHOOLS_PER_SUBMISSION = 20

SubmissionResultStatus = Literal["sent", "failed", "already_sent", "in_progress"]


class SubmissionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    school_ids: List[UUID] = Field(min_length=1, max_length=MAX_SCHOOLS_PER_SUBMISSION)


class SubmissionResult(BaseModel):
    school_id: UUID
    school_name: str
    status: SubmissionResultStatus
    error: Optional[str] = None


class SubmissionCreateResponse(BaseModel):
    results: List[SubmissionResult]
    sent_count: int
    student_copy_sent: bool


class SubmissionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    school_id: UUID
    school_name: str
    status: Literal["sending", "sent", "failed"]
    recipient_email: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
