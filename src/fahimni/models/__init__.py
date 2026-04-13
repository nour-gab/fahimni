"""ORM model package exports for metadata registration."""

from fahimni.models.archive_resource import ArchiveDifficulty, ArchiveResource, ArchiveResourceType
from fahimni.models.announcement import Announcement
from fahimni.models.assignment import Assignment
from fahimni.models.course import Course
from fahimni.models.course_material import CourseMaterial, MaterialSourceType, MaterialType
from fahimni.models.enrollment import Enrollment
from fahimni.models.grade import Grade
from fahimni.models.learning_event import LearningEvent, LearningEventType
from fahimni.models.message import Message
from fahimni.models.user_progress import UserProgress
from fahimni.models.user import User, UserRole

__all__ = [
	"Announcement",
	"ArchiveDifficulty",
	"ArchiveResource",
	"ArchiveResourceType",
	"Assignment",
	"Course",
	"CourseMaterial",
	"Enrollment",
	"Grade",
	"LearningEvent",
	"LearningEventType",
	"MaterialSourceType",
	"MaterialType",
	"Message",
	"User",
	"UserProgress",
	"UserRole",
]
