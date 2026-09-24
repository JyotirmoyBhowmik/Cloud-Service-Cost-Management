"""
Alert & Governance Policy Schemas
Strict DTOs for alert lifecycle tracking and governance policies.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AlertStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(OPEN|ACKNOWLEDGED|RESOLVED)$")
    resolution_notes: Optional[str] = None


class AlertResponse(BaseModel):
    id: str
    resource_id: Optional[str] = None
    budget_id: Optional[str] = None
    connector_id: Optional[str] = None
    alert_type: str
    severity: str
    status: str
    title: str
    message: str
    observed_value: Optional[float] = None
    threshold_value: Optional[float] = None
    unit: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyResponse(BaseModel):
    id: str
    name: str
    policy_class: str
    description: Optional[str] = None
    severity: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
