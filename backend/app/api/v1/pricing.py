"""
Pricing Intelligence & Simulation API
Implements rate catalog inspection and the interactive 'What Will This Cost?' simulator per User Request §3, §4, §53, §54.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service_pricing import PricingSKU
from app.schemas.service_pricing import PricingSKUResponse
from app.schemas.cost import WhatIfRequest, WhatIfResponse
from app.services.cost_engine import CostEngine

router = APIRouter(prefix="/pricing", tags=["Pricing Intelligence & Simulation"])


@router.get("/skus", response_model=List[PricingSKUResponse])
def list_pricing_skus(
    provider: Optional[str] = Query(None, description="AZURE, AWS, GCP, OCI"),
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lists official rate catalog SKUs across cloud providers."""
    query = db.query(PricingSKU)
    if provider and provider != "ALL":
        query = query.filter(PricingSKU.provider == provider.upper())
    if region:
        query = query.filter(PricingSKU.region == region)
    return query.all()


@router.post("/what-if", response_model=WhatIfResponse)
def simulate_what_if_cost(request: WhatIfRequest, db: Session = Depends(get_db)):
    """
    Interactive 'What Will This Cost?' simulation engine.
    Calculates hourly, daily, monthly, and annualized costs with full formula transparency per User Request §53 & §54.
    """
    return CostEngine.simulate_what_if(db, request)
