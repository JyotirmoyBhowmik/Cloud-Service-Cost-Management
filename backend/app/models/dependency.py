"""
Dependency & Service Topology Models
Implements directed service relationships and cost roll-up links per User Request §30, §31, §32.
"""

from sqlalchemy import Column, String, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class DependencyEdge(Base, TimestampMixin):
    __tablename__ = "dependency_edges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_node_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(String(36), ForeignKey("resource_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationship Taxonomy per BBP §533-550 & User Req §30
    edge_type = Column(String(50), default="DEPENDS_ON", nullable=False, index=True)
    # Types: DEPENDS_ON, CONNECTS_TO, SENDS_DATA_TO, RECEIVES_DATA_FROM, SHARED_BY, SECURED_BY, HOSTED_ON, USES, BILLS_TO
    
    confidence_score = Column(Float, default=1.0)  # 0.0 to 1.0
    cost_allocation_pct = Column(Float, default=100.0)  # Percentage of target cost attributed to source in total chain
    source_type = Column(String(50), default="MANUAL_OVERLAY")  # NATIVE_DISCOVERY, NETWORK_MAPPING, MANUAL_OVERLAY
    metadata_json = Column(JSON, default=dict)

    source_node = relationship("ResourceNode", foreign_keys=[source_node_id], backref="outgoing_dependencies")
    target_node = relationship("ResourceNode", foreign_keys=[target_node_id], backref="incoming_dependencies")

    __table_args__ = (
        Index("ix_depedge_src_tgt", "source_node_id", "target_node_id"),
    )
