"""Assignment and grades router endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.core.dependencies import get_current_user, require_role
from fahimni.db.repositories.grade_repository import GradeRepository
from fahimni.db.session import get_db
from fahimni.models.user import User, UserRole
from fahimni.schemas.grade import (
    AssignmentCreate,
    AssignmentResponse,
    GradeCreate,
    GradeResponse,
)

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    payload: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
) -> AssignmentResponse:
    repository = GradeRepository(db)
    try:
        assignment = await repository.create_assignment(
            course_id=uuid.UUID(payload.course_id),
            title=payload.title,
            description=payload.description,
            total_points=payload.total_points,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid course id") from exc
    return AssignmentResponse.model_validate(assignment)


@router.post("", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def post_grade(
    payload: GradeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
) -> GradeResponse:
    repository = GradeRepository(db)
    try:
        grade = await repository.create_grade(
            assignment_id=uuid.UUID(payload.assignment_id),
            student_id=uuid.UUID(payload.student_id),
            score=payload.score,
            feedback=payload.feedback,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ids") from exc
    return GradeResponse.model_validate(grade)


@router.get("/me", response_model=list[GradeResponse])
async def my_grades(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GradeResponse]:
    repository = GradeRepository(db)
    grades = await repository.list_grades_for_student(current_user.id)
    return [GradeResponse.model_validate(item) for item in grades]
