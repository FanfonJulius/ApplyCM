from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.dependencies import get_db
from app.schemas.program import Program, ProgramCreate
from app.services.program_service import ProgramService

router = APIRouter(prefix="/programs", tags=["programs"])

@router.get("/", response_model=List[Program])
def list_programs(
    school_id: Optional[UUID] = Query(None, description="Filter programs by school ID"),
    field_of_study: Optional[str] = Query(None, description="Filter by field of study"),
    degree_type: Optional[str] = Query(None, description="Filter by degree type"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return ProgramService.list_programs(
        db,
        school_id=school_id,
        field_of_study=field_of_study,
        degree_type=degree_type,
        skip=skip,
        limit=limit
    )

@router.get("/{program_id}", response_model=Program)
def get_program(program_id: UUID, db: Session = Depends(get_db)):
    program = ProgramService.get_program(db, program_id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program

@router.post("/", response_model=Program, status_code=status.HTTP_201_CREATED)
def create_program(program_in: ProgramCreate, db: Session = Depends(get_db)):
    return ProgramService.create_program(db, program_in=program_in)