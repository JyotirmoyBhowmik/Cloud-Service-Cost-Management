"""
Hierarchy & Canonical Resource Node Model
Represents multi-cloud native and normalized resource structures per BBP §318-360.
"""

from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid


class ResourceNode(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "resource_nodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    canonical_id = Column(String(255), unique=True, nullable=False, index=True)
    native_id = Column(String(512), nullable=False, index=True)
    connector_id = Column(String(36), ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False, index=True)  # AZURE, AWS, GCP, OCI
    name = Column(String(255), nullable=False, index=True)
    
    # Native and canonical taxonomy
    native_type = Column(String(100), nullable=False)
    canonical_role = Column(String(50), nullable=False)  # GOVERNANCE_ROOT, GOVERNANCE_GROUP, BILLING_CONTEXT, RESOURCE_CONTAINER, RESOURCE
    
    # Tree Lineage
    parent_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="SET NULL"), nullable=True, index=True)
    hierarchy_path = Column(String(1000), nullable=True)  # e.g. /Tenant/MG-Core/Sub-Prod/RG-App
    
    # Placement & Metadata
    region = Column(String(50), nullable=True, index=True)
    availability_zone = Column(String(50), nullable=True)
    environment = Column(String(50), default="production", index=True)
    owner = Column(String(150), nullable=True)
    business_unit = Column(String(100), nullable=True)
    cost_center = Column(String(100), nullable=True)
    tags = Column(JSON, default=dict)
    
    # Service & Financial Flags
    service_id = Column(String(36), ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)
    pricing_status = Column(String(30), default="ESTIMATED", index=True)  # FREE, FREE_TIER, CONDITIONAL_FREE, PAID, ESTIMATED, UNKNOWN, NOT_APPLICABLE
    threshold_state = Column(String(20), default="GREEN", index=True)     # GREEN, AMBER, ORANGE, RED, GREY
    
    # Lineage and Freshness
    last_sync_at = Column(DateTime, nullable=True)
    data_source = Column(String(50), default="API")
    native_metadata = Column(JSON, default=dict)

    # Relationships
    connector = relationship("Connector", back_populates="nodes")
    service = relationship("Service", back_populates="resources")
    parent = relationship("ResourceNode", remote_side=[id], backref="children")
    
    cost_records = relationship("CostRecord", back_populates="resource", cascade="all, delete-orphan")
    usage_metrics = relationship("UsageMetric", back_populates="resource", cascade="all, delete-orphan")
    runtime_records = relationship("RuntimeRecord", back_populates="resource", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="resource", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_resourcenodes_provider_canonical", "provider", "canonical_id"),
        Index("ix_resourcenodes_env_bu", "environment", "business_unit"),
    )
