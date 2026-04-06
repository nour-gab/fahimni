"""Repository for courses and enrollments."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.models.course import Course
from fahimni.models.enrollment import Enrollment


class CourseRepository:
    """Data access layer for course-related entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_course(
        self,
        *,
        title: str,
        code: str,
        description: str,
        professor_id: uuid.UUID,
    ) -> Course:
        course = Course(
            title=title,
            code=code,
            description=description,
            professor_id=professor_id,
        )
        self.db.add(course)
        await self.db.flush()
        await self.db.refresh(course)
        return course

    async def list_courses_for_user(self, user_id: uuid.UUID) -> list[Course]:
        own_result = await self.db.execute(select(Course).where(Course.professor_id == user_id))
        own_courses = list(own_result.scalars().all())

        enrolled_result = await self.db.execute(
            select(Course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == user_id)
        )
        enrolled_courses = list(enrolled_result.scalars().all())

        merged: dict[uuid.UUID, Course] = {course.id: course for course in own_courses}
        merged.update({course.id: course for course in enrolled_courses})
        return list(merged.values())

    async def enroll_student(self, course_id: uuid.UUID, student_id: uuid.UUID) -> Enrollment:
        enrollment = Enrollment(course_id=course_id, student_id=student_id)
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment
