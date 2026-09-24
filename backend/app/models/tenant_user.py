"""
Tenant & User Models
Implements multi-tenant boundary, user credentials, and enterprise RBAC.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid


class Tenant(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    default_currency = Column(String(3), default="USD", nullable=False)
    settings = Column(JSON, default=dict)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    connectors = relationship("Connector", back_populates="tenant", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="tenant", cascade="all, delete-orphan")


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="READ_ONLY", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    preferences = Column(JSON, default=dict)

    tenant = relationship("Tenant", back_populates="users")
