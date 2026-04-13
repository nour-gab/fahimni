"""add material archive progress event tables

Revision ID: 1d9f2bafc1a0
Revises: 969fd146ec67
Create Date: 2026-04-13 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1d9f2bafc1a0"
down_revision: Union[str, Sequence[str], None] = "969fd146ec67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "course_materials",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "material_type",
            sa.Enum("PDF", "IMAGE", "NOTES", "ARCHIVE", name="materialtype"),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum("TEACHER", "STUDENT", "ARCHIVE", name="materialsourcetype"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("storage_url", sa.String(length=1024), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_course_materials_course_id"), "course_materials", ["course_id"], unique=False)
    op.create_index(op.f("ix_course_materials_is_verified"), "course_materials", ["is_verified"], unique=False)
    op.create_index(op.f("ix_course_materials_year"), "course_materials", ["year"], unique=False)

    op.create_table(
        "archive_resources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("material_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "resource_type",
            sa.Enum("EXAM", "TD", "SUMMARY", name="archiveresourcetype"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("university", sa.String(length=255), nullable=False),
        sa.Column("professor", sa.String(length=255), nullable=True),
        sa.Column(
            "difficulty",
            sa.Enum("EASY", "MEDIUM", "HARD", name="archivedifficulty"),
            nullable=False,
        ),
        sa.Column("file_url", sa.String(length=1024), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["material_id"], ["course_materials.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_archive_resources_course_id"), "archive_resources", ["course_id"], unique=False)
    op.create_index(op.f("ix_archive_resources_material_id"), "archive_resources", ["material_id"], unique=False)
    op.create_index(op.f("ix_archive_resources_processed"), "archive_resources", ["processed"], unique=False)
    op.create_index(op.f("ix_archive_resources_year"), "archive_resources", ["year"], unique=False)

    op.create_table(
        "user_progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "course_id", "topic", name="uq_user_progress_topic"),
    )
    op.create_index(op.f("ix_user_progress_course_id"), "user_progress", ["course_id"], unique=False)
    op.create_index(op.f("ix_user_progress_user_id"), "user_progress", ["user_id"], unique=False)

    op.create_table(
        "learning_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "QUESTION_ASKED",
                "QUIZ_TAKEN",
                "MISTAKE_RECORDED",
                "MATERIAL_UPLOADED",
                name="learningeventtype",
            ),
            nullable=False,
        ),
        sa.Column("topic", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_learning_events_course_id"), "learning_events", ["course_id"], unique=False)
    op.create_index(op.f("ix_learning_events_user_id"), "learning_events", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_learning_events_user_id"), table_name="learning_events")
    op.drop_index(op.f("ix_learning_events_course_id"), table_name="learning_events")
    op.drop_table("learning_events")

    op.drop_index(op.f("ix_user_progress_user_id"), table_name="user_progress")
    op.drop_index(op.f("ix_user_progress_course_id"), table_name="user_progress")
    op.drop_table("user_progress")

    op.drop_index(op.f("ix_archive_resources_year"), table_name="archive_resources")
    op.drop_index(op.f("ix_archive_resources_processed"), table_name="archive_resources")
    op.drop_index(op.f("ix_archive_resources_material_id"), table_name="archive_resources")
    op.drop_index(op.f("ix_archive_resources_course_id"), table_name="archive_resources")
    op.drop_table("archive_resources")

    op.drop_index(op.f("ix_course_materials_year"), table_name="course_materials")
    op.drop_index(op.f("ix_course_materials_is_verified"), table_name="course_materials")
    op.drop_index(op.f("ix_course_materials_course_id"), table_name="course_materials")
    op.drop_table("course_materials")