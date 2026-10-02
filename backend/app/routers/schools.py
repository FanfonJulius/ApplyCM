from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.school import School, SchoolCreate
from app.schemas.program import Program
from app.services.school_service import SchoolService
from app.services.program_service import ProgramService

router = APIRouter(prefix="/schools", tags=["schools"])

@router.get("", response_model=List[School])
@router.get("/", response_model=List[School], include_in_schema=False)
def list_schools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return SchoolService.list_schools(db, skip=skip, limit=limit)

@router.get("/{school_id}", response_model=School)
def get_school(school_id: UUID, db: Session = Depends(get_db)):
    school = SchoolService.get_school(db, school_id=school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school

@router.get("/{school_id}/programs", response_model=List[Program])
def get_school_programs(school_id: UUID, db: Session = Depends(get_db)):
    school = SchoolService.get_school(db, school_id=school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return ProgramService.list_programs(db, school_id=school_id)

@router.post("/", response_model=School, status_code=status.HTTP_201_CREATED)
def create_school(school_in: SchoolCreate, db: Session = Depends(get_db)):
    return SchoolService.create_school(db, school_in=school_in)