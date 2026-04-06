"""Repository for assignments and grade records."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.models.assignment import Assignment
from fahimni.models.grade import Grade


class GradeRepository:
    """Data access layer for gradebook features."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_assignment(
        self,
        *,
        course_id: uuid.UUID,
        title: str,
        description: str,
        total_points: float,
    ) -> Assignment:
        assignment = Assignment(
            course_id=course_id,
            title=title,
            description=description,
            total_points=total_points,
        )
        self.db.add(assignment)
        await self.db.flush()
        await self.db.refresh(assignment)
        return assignment

    async def create_grade(
        self,
        *,
        assignment_id: uuid.UUID,
        student_id: uuid.UUID,
        score: float,
        feedback: str,
    ) -> Grade:
        grade = Grade(
            assignment_id=assignment_id,
            student_id=student_id,
            score=score,
            feedback=feedback,
        )
        self.db.add(grade)
        await self.db.flush()
        await self.db.refresh(grade)
        return grade

    async def list_grades_for_student(self, student_id: uuid.UUID) -> list[Grade]:
        result = await self.db.execute(
            select(Grade).where(Grade.student_id == student_id).order_by(Grade.updated_at.desc())
        )
        return list(result.scalars().all())

    async def list_assignments_for_course(self, course_id: uuid.UUID) -> list[Assignment]:
        result = await self.db.execute(
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .order_by(Assignment.created_at.desc())
        )
        return list(result.scalars().all())
