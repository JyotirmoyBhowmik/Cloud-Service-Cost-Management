"""
Cost & Financial Reconciliation Models
Complies with FinOps FOCUS 1.4 specification and User Request §7, §8, §49.
"""

from sqlalchemy import Column, String, Float, ForeignKey, JSON, DateTime, Text, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class CostRecord(Base, TimestampMixin):
    __tablename__ = "cost_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    sku_id = Column(String(36), ForeignKey("pricing_skus.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(20), nullable=False, index=True)
    billing_account_id = Column(String(100), nullable=False, index=True)
    
    # FOCUS 1.4 Core Charge Dimensions
    cost_state = Column(String(30), default="ACTUAL", nullable=False, index=True)  # ACTUAL, ESTIMATED, FORECAST, MANUAL
    charge_category = Column(String(50), default="Usage")  # Usage, Purchase, Refund, Tax, Credit
    
    # Financial Quantities
    billed_cost = Column(Float, default=0.0, nullable=False)
    effective_cost = Column(Float, default=0.0, nullable=False)
    list_cost = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Usage metrics
    usage_quantity = Column(Float, default=0.0, nullable=False)
    usage_unit = Column(String(50), default="Hours")
    
    # Time Horizon
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Calculation & Transparency
    pricing_status = Column(String(30), default="PAID")
    calculation_method = Column(String(100), default="PROVIDER_INVOICE")  # PROVIDER_INVOICE, FORMULA_USAGE_X_RATE, RUN_RATE_PROJECTION
    raw_focus_attributes = Column(JSON, default=dict)

    resource = relationship("ResourceNode", back_populates="cost_records")
    sku = relationship("PricingSKU", back_populates="cost_records")

    __table_args__ = (
        Index("ix_costrecord_resource_period", "resource_id", "period_start", "period_end"),
        Index("ix_costrecord_provider_state", "provider", "cost_state"),
    )


class ReconciliationRecord(Base, TimestampMixin):
    __tablename__ = "reconciliation_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String(20), nullable=False, index=True)  # e.g. "2026-09"
    provider = Column(String(20), nullable=False)
    
    estimated_amount = Column(Float, default=0.0, nullable=False)
    actual_amount = Column(Float, default=0.0, nullable=False)
    difference = Column(Float, default=0.0, nullable=False)
    variance_pct = Column(Float, default=0.0, nullable=False)
    
    driver_type = Column(String(50), default="UNKNOWN")  # USAGE_DRIFT, RATE_CHANGE, DISCOUNT_APPLIED, NEW_METERS, TAXES_CREDITS
    status = Column(String(30), default="PENDING_REVIEW")  # RECONCILED, PENDING_REVIEW, ACCEPTED_VARIANCE, DISPUTED
    notes = Column(Text, nullable=True)

    resource = relationship("ResourceNode")


class ForecastRecord(Base, TimestampMixin):
    __tablename__ = "forecast_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scope_type = Column(String(50), nullable=False)  # RESOURCE, SERVICE, ACCOUNT, PROVIDER, TENANT
    scope_id = Column(String(100), nullable=False, index=True)
    forecast_period = Column(String(20), nullable=False, index=True)  # "2026-10"
    
    projected_amount = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    confidence_score = Column(Float, default=0.90)  # 0.0 - 1.0
    
    method = Column(String(50), default="RUN_RATE")  # RUN_RATE, MOVING_AVERAGE, SEASONAL_DECOMP
    historical_periods_evaluated = Column(Float, default=30)
    calculated_at = Column(DateTime, nullable=False)
