"""
Budget & Threshold Rule Schemas
Strict DTOs for financial budgets and multi-band threshold policies.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BudgetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    scope_type: str = Field(..., description="GLOBAL, PROVIDER, SUBSCRIPTION, ACCOUNT, PROJECT, COMPARTMENT, APP, BU")
    scope_id: str
    amount: float = Field(..., gt=0.0)
    currency: str = Field(default="USD", max_length=3)
    period: str = Field(default="MONTHLY")
    warning_threshold_pct: float = Field(default=75.0, ge=0.0, le=200.0)
    critical_threshold_pct: float = Field(default=100.0, ge=0.0, le=500.0)
    forecast_threshold_pct: float = Field(default=110.0, ge=0.0, le=500.0)
    parent_budget_id: Optional[str] = None
    owner_email: Optional[str] = None
    alert_emails: List[str] = Field(default_factory=list)


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    warning_threshold_pct: Optional[float] = None
    critical_threshold_pct: Optional[float] = None
    forecast_threshold_pct: Optional[float] = None
    owner_email: Optional[str] = None
    alert_emails: Optional[List[str]] = None


class BudgetResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    scope_type: str
    scope_id: str
    amount: float
    currency: str
    period: str
    warning_threshold_pct: float
    critical_threshold_pct: float
    forecast_threshold_pct: float
    current_spend: float
    forecasted_spend: float
    utilization_pct: float = 0.0
    parent_budget_id: Optional[str] = None
    owner_email: Optional[str] = None
    alert_emails: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class ThresholdRuleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    metric_name: str
    scope_type: str = "GLOBAL"
    scope_id: str = "*"
    operator: str = ">="
    green_max: float = 75.0
    amber_max: float = 90.0
    orange_max: float = 100.0
    red_min: float = 100.0
    hysteresis_buffer: float = 2.0


class ThresholdRuleResponse(BaseModel):
    id: str
    name: str
    metric_name: str
    scope_type: str
    scope_id: str
    operator: str
    green_max: float
    amber_max: float
    orange_max: float
    red_min: float
    hysteresis_buffer: float
    is_active: bool

    class Config:
        from_attributes = True
