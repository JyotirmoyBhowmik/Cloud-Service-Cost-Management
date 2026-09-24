"""
Usage & Runtime Monitoring Models
Implements consumption metrics and runtime profiles per User Request §28, §29 and BBP §424-462.
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class UsageMetric(Base, TimestampMixin):
    __tablename__ = "usage_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)  # CPU_UTILIZATION, MEMORY_UTILIZATION, STORAGE_GB, NETWORK_EGRESS_GB, REQUESTS
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=False)  # %, GB, IOPS, Count
    recorded_at = Column(DateTime, nullable=False, index=True)
    source = Column(String(50), default="TELEMETRY")  # AZURE_MONITOR, CLOUDWATCH, CLOUD_MONITORING, OCI_MONITORING

    resource = relationship("ResourceNode", back_populates="usage_metrics")

    __table_args__ = (
        Index("ix_usagemetric_res_metric_time", "resource_id", "metric_name", "recorded_at"),
    )


class RuntimeRecord(Base, TimestampMixin):
    __tablename__ = "runtime_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    runtime_profile = Column(String(50), default="24x7", nullable=False)  # 24x7, SCHEDULED, SEASONAL, EVENT_DRIVEN, CONSUMPTION
    is_running = Column(Boolean, default=True, nullable=False)
    
    # Hours & Schedules
    active_hours_today = Column(Float, default=24.0)
    active_hours_monthly = Column(Float, default=720.0)
    expected_hours_monthly = Column(Float, default=720.0)
    schedule_definition = Column(JSON, default=dict)  # {"days": ["Mon-Fri"], "hours": "08:00-18:00"}
    
    # Drift and exceptions
    schedule_adherence_pct = Column(Float, default=100.0)
    drift_hours_detected = Column(Float, default=0.0)
    last_state_change = Column(DateTime, nullable=True)

    resource = relationship("ResourceNode", back_populates="runtime_records")
