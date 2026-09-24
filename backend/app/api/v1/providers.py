"""
Cloud Provider Endpoints
Provides provider summaries, estate counts, and native hierarchy roll-ups per User Request §23.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.hierarchy import ResourceNode
from app.models.cost import CostRecord
from app.models.budget_threshold import Budget
from app.models.connector import Connector

router = APIRouter(prefix="/providers", tags=["Cloud Providers"])


@router.get("")
def list_providers(db: Session = Depends(get_db)):
    """Lists supported cloud providers with live resource counts and aggregated spend."""
    providers = ["AZURE", "AWS", "GCP", "OCI"]
    result = []
    
    for prov in providers:
        res_count = db.query(ResourceNode).filter(ResourceNode.provider == prov, ResourceNode.canonical_role == "RESOURCE").count()
        spend = db.query(func.coalesce(func.sum(CostRecord.billed_cost), 0.0)).filter(CostRecord.provider == prov).scalar() or 0.0
        conn = db.query(Connector).filter(Connector.provider == prov).first()
        budget = db.query(Budget).filter(Budget.scope_type == "PROVIDER", Budget.scope_id == prov).first()

        result.append({
            "provider": prov,
            "display_name": {
                "AZURE": "Microsoft Azure",
                "AWS": "Amazon Web Services",
                "GCP": "Google Cloud Platform",
                "OCI": "Oracle Cloud Infrastructure",
            }.get(prov, prov),
            "status": conn.status if conn else "NOT_CONFIGURED",
            "resource_count": res_count,
            "service_count": 4,
            "monthly_spend": round(spend, 2),
            "budget_amount": round(budget.amount, 2) if budget else 0.0,
            "budget_utilization_pct": round((spend / budget.amount) * 100.0, 1) if budget and budget.amount > 0 else 0.0,
            "currency": "USD",
            "last_sync": conn.last_successful_sync if conn else None,
            "freshness": "Current (15m ago)",
        })
    return result


@router.get("/{provider}/overview")
def get_provider_overview(provider: str, db: Session = Depends(get_db)):
    """Detailed provider cockpit metrics for Azure, AWS, GCP, or OCI."""
    prov_upper = provider.upper()
    if prov_upper not in ["AZURE", "AWS", "GCP", "OCI"]:
        raise HTTPException(status_code=404, detail="Cloud provider not supported.")

    resources = db.query(ResourceNode).filter(ResourceNode.provider == prov_upper).all()
    conn = db.query(Connector).filter(Connector.provider == prov_upper).first()
    spend = db.query(func.coalesce(func.sum(CostRecord.billed_cost), 0.0)).filter(CostRecord.provider == prov_upper).scalar() or 0.0
    budget = db.query(Budget).filter(Budget.scope_type == "PROVIDER", Budget.scope_id == prov_upper).first()

    return {
        "provider": prov_upper,
        "connector": {
            "name": conn.name if conn else "Default Adapter",
            "status": conn.status if conn else "UNKNOWN",
            "auth_method": conn.auth_method if conn else "N/A",
            "last_sync": conn.last_successful_sync if conn else None,
        },
        "metrics": {
            "total_nodes": len(resources),
            "resource_count": sum(1 for r in resources if r.canonical_role == "RESOURCE"),
            "monthly_spend": round(spend, 2),
            "budget_amount": round(budget.amount, 2) if budget else 0.0,
            "budget_utilization_pct": round((spend / budget.amount) * 100.0, 1) if budget and budget.amount > 0 else 0.0,
            "currency": "USD",
        },
        "native_hierarchy_preview": [
            {"id": r.id, "name": r.name, "native_type": r.native_type, "role": r.canonical_role, "pricing_status": r.pricing_status}
            for r in resources[:8]
        ]
    }
