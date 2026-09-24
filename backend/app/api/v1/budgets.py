"""
Budget Management API
Implements hierarchical budget creation, tracking, and breach alerts per User Request §25.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.budget_threshold import Budget
from app.schemas.budget_threshold import BudgetCreate, BudgetUpdate, BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budget Engine"])


@router.get("", response_model=List[BudgetResponse])
def list_budgets(db: Session = Depends(get_db)):
    """Lists all configured budgets with current spend and utilization percentages."""
    budgets = db.query(Budget).filter(Budget.is_deleted == False).all()
    results = []
    for b in budgets:
        utilization = (b.current_spend / b.amount) * 100.0 if b.amount > 0 else 0.0
        dto = BudgetResponse.model_validate(b)
        dto.utilization_pct = round(utilization, 1)
        results.append(dto)
    return results


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    """Creates a new hierarchical budget."""
    # Obtain tenant
    tenant_id = "tenant-default-001"
    first_b = db.query(Budget).first()
    if first_b:
        tenant_id = first_b.tenant_id

    budget = Budget(
        tenant_id=tenant_id,
        name=payload.name,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        amount=payload.amount,
        currency=payload.currency,
        period=payload.period,
        warning_threshold_pct=payload.warning_threshold_pct,
        critical_threshold_pct=payload.critical_threshold_pct,
        forecast_threshold_pct=payload.forecast_threshold_pct,
        parent_budget_id=payload.parent_budget_id,
        owner_email=payload.owner_email,
        alert_emails=payload.alert_emails,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    # Evaluate spend immediately
    BudgetService.recalculate_budget_utilization(db, budget.id)
    dto = BudgetResponse.model_validate(budget)
    dto.utilization_pct = 0.0
    return dto


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: str, payload: BudgetUpdate, db: Session = Depends(get_db)):
    """Updates an existing budget target and recalculates thresholds."""
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.is_deleted == False).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(budget, field, val)

    db.commit()
    db.refresh(budget)
    BudgetService.recalculate_budget_utilization(db, budget.id)
    
    dto = BudgetResponse.model_validate(budget)
    dto.utilization_pct = round((budget.current_spend / budget.amount) * 100.0, 1) if budget.amount > 0 else 0.0
    return dto
