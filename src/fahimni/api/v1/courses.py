"""Course and enrollment router endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.core.dependencies import get_current_user, require_role
from fahimni.db.repositories.course_repository import CourseRepository
from fahimni.db.session import get_db
from fahimni.models.user import User, UserRole
from fahimni.schemas.course import CourseCreate, CourseResponse, EnrollmentCreate

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
    current_user: User = Depends(get_current_user),
) -> CourseResponse:
    repository = CourseRepository(db)
    course = await repository.create_course(
        title=payload.title,
        code=payload.code,
        description=payload.description,
        professor_id=current_user.id,
    )
    return CourseResponse.model_validate(course)


@router.get("", response_model=list[CourseResponse])
async def list_my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CourseResponse]:
    repository = CourseRepository(db)
    courses = await repository.list_courses_for_user(current_user.id)
    return [CourseResponse.model_validate(item) for item in courses]


@router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_student(
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
) -> dict[str, str]:
    repository = CourseRepository(db)
    try:
        enrollment = await repository.enroll_student(
            course_id=uuid.UUID(payload.course_id),
            student_id=uuid.UUID(payload.student_id),
        )
        return {"enrollment_id": str(enrollment.id)}
    except (IntegrityError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid enrollment") from exc
