"""
Dependency & Topology Graph Schemas
Implements interactive graph models and cost-aware dependency chains per User Request §30, §31, §32.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DependencyNodeDTO(BaseModel):
    id: str
    canonical_id: str
    name: str
    provider: str
    service_name: str
    service_family: str
    environment: str
    direct_cost: float
    dependent_cost: float
    total_cost: float
    currency: str = "USD"
    threshold_state: str
    pricing_status: str


class DependencyEdgeDTO(BaseModel):
    id: str
    source_id: str
    target_id: str
    edge_type: str  # DEPENDS_ON, CONNECTS_TO, SENDS_DATA_TO, SHARED_BY, HOSTED_ON, BILLS_TO
    confidence_score: float
    cost_allocation_pct: float


class DependencyGraphResponse(BaseModel):
    nodes: List[DependencyNodeDTO]
    edges: List[DependencyEdgeDTO]
    total_graph_cost: float
    currency: str = "USD"
    cluster_count: int


class DependencyEdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    edge_type: str = Field(default="DEPENDS_ON")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    cost_allocation_pct: float = Field(default=100.0, ge=0.0, le=100.0)
