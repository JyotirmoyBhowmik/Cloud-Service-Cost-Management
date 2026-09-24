"""
Cost, Reconciliation & What-If Simulator Schemas
Implements FOCUS 1.4-aligned reporting, variance reconciliation, and cost simulation per User Request §6, §7, §8, §53.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CostRecordResponse(BaseModel):
    id: str
    resource_id: str
    sku_id: Optional[str] = None
    provider: str
    billing_account_id: str
    cost_state: str  # ACTUAL, ESTIMATED, FORECAST, MANUAL
    charge_category: str
    billed_cost: float
    effective_cost: float
    list_cost: float
    currency: str
    usage_quantity: float
    usage_unit: str
    period_start: datetime
    period_end: datetime
    pricing_status: str
    calculation_method: str

    class Config:
        from_attributes = True


class CostDriverBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float


class CostSummaryResponse(BaseModel):
    total_cost: float
    actual_cost: float
    estimated_cost: float
    forecast_cost: float
    budget_amount: float
    budget_utilization_pct: float
    variance_amount: float
    variance_pct: float
    currency: str = "USD"
    
    # Aggregated Breakdowns
    by_provider: Dict[str, float]
    by_service_family: Dict[str, float]
    by_environment: Dict[str, float]
    top_cost_drivers: List[CostDriverBreakdown]


class ReconciliationResponse(BaseModel):
    id: str
    resource_id: str
    resource_name: str
    provider: str
    period: str
    estimated_amount: float
    actual_amount: float
    difference: float
    variance_pct: float
    driver_type: str  # USAGE_DRIFT, RATE_CHANGE, DISCOUNT_APPLIED, NEW_METERS, TAXES_CREDITS
    status: str       # RECONCILED, PENDING_REVIEW, ACCEPTED_VARIANCE, DISPUTED
    notes: Optional[str] = None
    created_at: datetime


class WhatIfRequest(BaseModel):
    """Payload for 'What Will This Cost?' interactive simulator."""
    provider: str = Field(..., pattern="^(AZURE|AWS|GCP|OCI)$")
    service_code: str
    sku_id: Optional[str] = None
    region: str = "us-east-1"
    quantity: int = Field(default=1, ge=1, le=1000)
    runtime_hours_per_day: float = Field(default=24.0, ge=0.0, le=24.0)
    days_per_month: int = Field(default=30, ge=1, le=31)
    storage_gb: float = Field(default=0.0, ge=0.0)
    network_egress_gb: float = Field(default=0.0, ge=0.0)
    requests_count: float = Field(default=0.0, ge=0.0)


class WhatIfResponse(BaseModel):
    provider: str
    service_name: str
    sku_name: str
    region: str
    hourly_cost: float
    daily_cost: float
    monthly_cost: float
    annual_cost: float
    currency: str = "USD"
    formula_explanation: str
    assumptions: List[str]
