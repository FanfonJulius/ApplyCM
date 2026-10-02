from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.program import Program
from app.schemas.program import ProgramCreate, ProgramUpdate

class ProgramService:
    @staticmethod
    def get_program(db: Session, program_id: UUID) -> Optional[Program]:
        return db.query(Program).filter(Program.id == program_id).first()

    @staticmethod
    def list_programs(
        db: Session,
        school_id: Optional[UUID] = None,
        field_of_study: Optional[str] = None,
        degree_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Program]:
        query = db.query(Program)
        if school_id:
            query = query.filter(Program.school_id == school_id)
        if field_of_study:
            query = query.filter(Program.field_of_study.ilike(f"%{field_of_study}%"))
        if degree_type:
            query = query.filter(Program.degree_type.ilike(f"%{degree_type}%"))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_program(db: Session, program_in: ProgramCreate) -> Program:
        db_program = Program(**program_in.model_dump())
        db.add(db_program)
        db.commit()
        db.refresh(db_program)
        return db_program