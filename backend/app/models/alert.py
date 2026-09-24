"""
Alert & Governance Policy Models
Implements complete alert lifecycle and policy enforcement per User Request §33 and BBP §1226-1241.
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, DateTime, Text, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid


class Alert(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=True, index=True)
    connector_id = Column(String(36), ForeignKey("connectors.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Alert Category & Severity
    alert_type = Column(String(50), nullable=False, index=True)  # BUDGET_BREACH, FORECAST_BREACH, COST_SPIKE, RUNTIME_DRIFT, STALE_DATA
    severity = Column(String(20), default="WARNING", nullable=False, index=True)  # INFO, WARNING, CRITICAL
    status = Column(String(20), default="OPEN", nullable=False, index=True)       # CREATED, OPEN, ACKNOWLEDGED, RESOLVED
    
    # Details & Metrics
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    observed_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    unit = Column(String(30), nullable=True)
    
    # Lifecycle Auditing
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    resource = relationship("ResourceNode", back_populates="alerts")
    budget = relationship("Budget")
    connector = relationship("Connector")

    __table_args__ = (
        Index("ix_alert_status_sev", "status", "severity"),
    )


class Policy(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    policy_class = Column(String(50), nullable=False)  # METADATA, FINANCIAL, DATA, CONNECTOR, TOPOLOGY
    description = Column(Text, nullable=True)
    rule_definition = Column(JSON, nullable=False)  # {"field": "tags.owner", "operator": "exists"}
    severity = Column(String(20), default="WARNING")
    is_active = Column(Boolean, default=True)
