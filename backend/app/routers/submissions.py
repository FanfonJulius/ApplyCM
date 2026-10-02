from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.submission import SubmissionCreateRequest, SubmissionCreateResponse, SubmissionItem
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("", response_model=List[SubmissionItem])
def list_my_submissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Where the signed-in student's application PDF has been emailed, per university."""
    return SubmissionService.list_submissions(db, user_id=current_user.id)


@router.post("", response_model=SubmissionCreateResponse)
def submit_application(
    body: SubmissionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Emails the student's application profile PDF to the chosen favorite universities.

    Requires the Profile, Contact, Education, Activities and Writing sections.
    Universities that already received it are skipped; failed sends can be retried.
    The student is emailed a copy when at least one university was sent to.
    """
    return SubmissionService.submit(db, user=current_user, school_ids=body.school_ids)
