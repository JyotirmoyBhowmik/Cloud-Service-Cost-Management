"""
Connector & Sync Job Models
Represents cloud provider registrations, health states, encrypted credentials, and sync history.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid


class Connector(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "connectors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False, index=True)  # AZURE, AWS, GCP, OCI
    name = Column(String(100), nullable=False)
    auth_method = Column(String(50), nullable=False)  # SERVICE_PRINCIPAL, IAM_ROLE, SERVICE_ACCOUNT, API_KEY, DEMO
    status = Column(String(30), default="CONNECTED", nullable=False)
    
    # Encrypted secrets via AES-256-GCM
    encrypted_credentials = Column(Text, nullable=True)
    config = Column(JSON, default=dict)  # Tenant ID, Subscriptions, Regions, OUs, Compartments
    
    # Telemetry and status
    last_successful_sync = Column(DateTime, nullable=True)
    last_attempted_sync = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    resource_count = Column(Integer, default=0)
    service_count = Column(Integer, default=0)
    pricing_status = Column(String(30), default="HEALTHY")
    cost_status = Column(String(30), default="HEALTHY")
    usage_status = Column(String(30), default="HEALTHY")

    tenant = relationship("Tenant", back_populates="connectors")
    sync_jobs = relationship("SyncJob", back_populates="connector", cascade="all, delete-orphan")
    nodes = relationship("ResourceNode", back_populates="connector", cascade="all, delete-orphan")


class SyncJob(Base, TimestampMixin):
    __tablename__ = "sync_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    connector_id = Column(String(36), ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # HIERARCHY, INVENTORY, PRICING, COST, USAGE, RUNTIME, DEPENDENCY, FULL
    status = Column(String(30), default="PENDING", nullable=False)  # PENDING, RUNNING, COMPLETED, FAILED, PARTIAL
    records_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)

    connector = relationship("Connector", back_populates="sync_jobs")
