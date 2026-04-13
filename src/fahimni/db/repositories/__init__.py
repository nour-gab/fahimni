"""Repository package exports."""

from fahimni.db.repositories.announcement_repository import AnnouncementRepository
from fahimni.db.repositories.course_repository import CourseRepository
from fahimni.db.repositories.grade_repository import GradeRepository
from fahimni.db.repositories.material_repository import MaterialRepository
from fahimni.db.repositories.message_repository import MessageRepository
from fahimni.db.repositories.user_repository import UserRepository

__all__ = [
    "AnnouncementRepository",
    "CourseRepository",
    "GradeRepository",
    "MaterialRepository",
    "MessageRepository",
    "UserRepository",
]
