"""ORM model package exports for metadata registration."""

from fahimni.models.announcement import Announcement
from fahimni.models.assignment import Assignment
from fahimni.models.course import Course
from fahimni.models.enrollment import Enrollment
from fahimni.models.grade import Grade
from fahimni.models.message import Message
from fahimni.models.user import User, UserRole

__all__ = [
	"Announcement",
	"Assignment",
	"Course",
	"Enrollment",
	"Grade",
	"Message",
	"User",
	"UserRole",
]
