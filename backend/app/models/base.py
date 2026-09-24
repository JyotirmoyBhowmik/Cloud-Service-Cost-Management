"""
Base Model & Mixins
Provides audit fields, timestamps, and soft-delete capabilities.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean, String
import uuid


def generate_uuid() -> str:
    """Generates standard UUID4 string."""
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
