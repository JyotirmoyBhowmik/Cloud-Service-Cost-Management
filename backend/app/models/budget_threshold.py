"""
Budget & Threshold Rule Models
Implements hierarchical financial budgets and configurable threshold state rules per User Request §25, §26, §27.
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid


class Budget(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    
    # Scoping
    scope_type = Column(String(50), nullable=False, index=True)  # GLOBAL, PROVIDER, SUBSCRIPTION, ACCOUNT, PROJECT, COMPARTMENT, APP, BU
    scope_id = Column(String(100), nullable=False, index=True)
    
    # Financial targets
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    period = Column(String(20), default="MONTHLY", nullable=False)  # MONTHLY, QUARTERLY, ANNUAL
    
    # Threshold trigger bands
    warning_threshold_pct = Column(Float, default=75.0)
    critical_threshold_pct = Column(Float, default=100.0)
    forecast_threshold_pct = Column(Float, default=110.0)
    
    # Dynamic live roll-up aggregates
    current_spend = Column(Float, default=0.0)
    forecasted_spend = Column(Float, default=0.0)
    
    # Hierarchical roll-up
    parent_budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="SET NULL"), nullable=True)
    owner_email = Column(String(255), nullable=True)
    alert_emails = Column(JSON, default=list)

    tenant = relationship("Tenant", back_populates="budgets")
    parent_budget = relationship("Budget", remote_side=[id], backref="child_budgets")


class ThresholdRule(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "threshold_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    
    # Metric and Target Scope
    metric_name = Column(String(100), nullable=False, index=True)  # budget_utilization_pct, monthly_cost, cpu_utilization, runtime_drift
    scope_type = Column(String(50), default="GLOBAL")
    scope_id = Column(String(100), default="*")
    operator = Column(String(10), default=">=")
    
    # Color State Band Cutoffs (Configurable per User Request §26)
    green_max = Column(Float, default=75.0)
    amber_max = Column(Float, default=90.0)
    orange_max = Column(Float, default=100.0)
    red_min = Column(Float, default=100.0)
    
    # Hysteresis buffer to avoid alert oscillation
    hysteresis_buffer = Column(Float, default=2.0)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_thresholdrule_tenant_metric", "tenant_id", "metric_name"),
    )
