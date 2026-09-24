"""
Connector & Onboarding Wizard Schemas
Implements connector configuration and the 16-step guided onboarding wizard per User Request §16, §17.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ConnectorCreate(BaseModel):
    provider: str = Field(..., pattern="^(AZURE|AWS|GCP|OCI)$")
    name: str = Field(..., min_length=2, max_length=100)
    auth_method: str = Field(default="SERVICE_PRINCIPAL")  # SERVICE_PRINCIPAL, IAM_ROLE, SERVICE_ACCOUNT, API_KEY, DEMO
    credentials: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)


class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ConnectorResponse(BaseModel):
    id: str
    tenant_id: str
    provider: str
    name: str
    auth_method: str
    status: str
    config: Dict[str, Any]
    last_successful_sync: Optional[datetime] = None
    last_attempted_sync: Optional[datetime] = None
    last_error: Optional[str] = None
    resource_count: int
    service_count: int
    pricing_status: str
    cost_status: str
    usage_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OnboardingValidateRequest(BaseModel):
    provider: str = Field(..., pattern="^(AZURE|AWS|GCP|OCI)$")
    auth_method: str
    connection_info: Dict[str, Any]
    step_number: int = Field(ge=1, le=16)


class OnboardingValidateResponse(BaseModel):
    step_number: int
    step_name: str
    is_valid: bool
    message: str
    discovered_items: Optional[List[Dict[str, Any]]] = None
    next_step: int
    details: Optional[Dict[str, Any]] = None
