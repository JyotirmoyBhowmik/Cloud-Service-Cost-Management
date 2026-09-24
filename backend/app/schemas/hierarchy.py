"""
Hierarchy & Resource Schemas
Strict DTOs for multi-cloud resource trees and canonical node operations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ResourceNodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., pattern="^(AZURE|AWS|GCP|OCI)$")
    native_id: str
    native_type: str
    canonical_role: str = Field(..., description="GOVERNANCE_ROOT, GOVERNANCE_GROUP, BILLING_CONTEXT, RESOURCE_CONTAINER, RESOURCE")
    parent_id: Optional[str] = None
    region: Optional[str] = None
    environment: str = Field(default="production")
    owner: Optional[str] = None
    business_unit: Optional[str] = None
    cost_center: Optional[str] = None
    tags: Dict[str, Any] = Field(default_factory=dict)
    service_id: Optional[str] = None
    pricing_status: str = Field(default="ESTIMATED")
    threshold_state: str = Field(default="GREEN")


class ResourceNodeCreate(ResourceNodeBase):
    connector_id: str
    canonical_id: str


class ResourceNodeUpdate(BaseModel):
    name: Optional[str] = None
    environment: Optional[str] = None
    owner: Optional[str] = None
    business_unit: Optional[str] = None
    cost_center: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    pricing_status: Optional[str] = None
    threshold_state: Optional[str] = None


class ResourceCostSnapshot(BaseModel):
    hourly_cost: float = 0.0
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    annualized_cost: float = 0.0
    currency: str = "USD"
    cost_state: str = "ACTUAL"


class ResourceNodeResponse(ResourceNodeBase):
    id: str
    canonical_id: str
    connector_id: str
    hierarchy_path: Optional[str] = None
    data_source: str
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    cost_snapshot: Optional[ResourceCostSnapshot] = None

    class Config:
        from_attributes = True


class HierarchyTreeNode(BaseModel):
    id: str
    canonical_id: str
    name: str
    provider: str
    native_type: str
    canonical_role: str
    region: Optional[str] = None
    environment: str
    pricing_status: str
    threshold_state: str
    monthly_cost: float = 0.0
    currency: str = "USD"
    resource_count: int = 0
    children: List["HierarchyTreeNode"] = Field(default_factory=list)


HierarchyTreeNode.model_rebuild()


class HierarchySummaryResponse(BaseModel):
    total_nodes: int
    providers: Dict[str, int]
    by_canonical_role: Dict[str, int]
    by_environment: Dict[str, int]
    total_monthly_spend: float
    currency: str = "USD"
