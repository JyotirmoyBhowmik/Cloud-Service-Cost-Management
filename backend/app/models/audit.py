"""
Administrative Audit Trail Model
Implements immutable compliance and override audit logging per User Request §36 and BBP §1115-1132.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text, Index

from app.core.database import Base
from app.models.base import generate_uuid


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    
    # Action taxonomy
    action = Column(String(100), nullable=False, index=True)  # LOGIN, CONNECTOR_CREATE, BUDGET_UPDATE, OVERRIDE_APPLY
    entity_type = Column(String(50), nullable=False, index=True)  # ResourceNode, Budget, ThresholdRule, Connector
    entity_id = Column(String(100), nullable=False, index=True)
    
    # State transitions
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    
    # Client and tracing metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    correlation_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_entity_time", "entity_type", "entity_id", "created_at"),
    )
