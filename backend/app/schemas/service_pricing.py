"""
Service & Pricing Intelligence Schemas
Implements transparent rate catalogs and comprehensive ⓘ cost explanations per User Request §3, §4, §5, §52.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PricingTierDTO(BaseModel):
    tier_number: float
    start_amount: float
    end_amount: Optional[float] = None
    unit_price: float


class PricingSKUResponse(BaseModel):
    id: str
    service_id: str
    provider: str
    provider_sku_id: str
    sku_name: str
    meter_name: Optional[str] = None
    pricing_model: str
    billing_unit: str
    unit_price: float
    currency: str
    region: str
    is_free: bool
    free_allowance_units: float
    free_allowance_description: Optional[str] = None
    commitment_type: str
    effective_start: Optional[datetime] = None
    pricing_source: str
    tiers: List[PricingTierDTO] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ServiceResponse(BaseModel):
    id: str
    provider: str
    service_code: str
    service_name: str
    service_family: str
    category: Optional[str] = None
    description: Optional[str] = None
    default_pricing_model: str
    has_free_tier: bool
    free_tier_description: Optional[str] = None
    resource_count: int = 0
    skus: List[PricingSKUResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PricingExplanationResponse(BaseModel):
    """
    Detailed payload for the Information Icon (ⓘ) popover/modal.
    Answers: 'Why does this service cost this amount?' without leaving the screen.
    """
    resource_id: str
    resource_name: str
    provider: str
    service_name: str
    service_family: str
    pricing_status: str  # FREE, FREE_TIER, CONDITIONAL_FREE, PAID, ESTIMATED, UNKNOWN, NOT_APPLICABLE
    status_reason: str
    
    # SKU and Unit Rates
    provider_sku_id: Optional[str] = None
    sku_name: Optional[str] = None
    billing_unit: Optional[str] = None
    unit_price: float = 0.0
    currency: str = "USD"
    pricing_model: str
    region: Optional[str] = None
    
    # Free allowances & Commitments
    free_allowance: Optional[str] = None
    commitment_discount: Optional[str] = None
    
    # Mathematical Breakdown
    usage_quantity: float = 0.0
    usage_unit: str = "Hours"
    monthly_cost: float = 0.0
    cost_calculation_method: str
    calculation_formula: str
    
    # Transparency metadata
    assumptions_included: List[str] = Field(default_factory=list)
    assumptions_excluded: List[str] = Field(default_factory=list)
    pricing_source: str
    effective_date: Optional[str] = None
    retrieval_timestamp: Optional[datetime] = None
