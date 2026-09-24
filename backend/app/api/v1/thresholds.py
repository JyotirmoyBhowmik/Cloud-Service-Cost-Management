"""
Threshold & Color Policy API
Implements configurable threshold rule policies and simulation per User Request §26, §27.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.budget_threshold import ThresholdRule
from app.schemas.budget_threshold import ThresholdRuleCreate, ThresholdRuleResponse
from app.services.threshold_engine import ThresholdEngine

router = APIRouter(prefix="/thresholds", tags=["Threshold Policy Engine"])


@router.get("/rules", response_model=List[ThresholdRuleResponse])
def list_threshold_rules(db: Session = Depends(get_db)):
    """Lists configured threshold color state bands and hysteresis settings."""
    rules = db.query(ThresholdRule).filter(ThresholdRule.is_deleted == False).all()
    if not rules:
        # Provide default rule
        return [
            ThresholdRuleResponse(
                id="default-rule-001",
                name="Default Enterprise Multi-Band Rule",
                metric_name="budget_utilization_pct",
                scope_type="GLOBAL",
                scope_id="*",
                operator=">=",
                green_max=75.0,
                amber_max=90.0,
                orange_max=100.0,
                red_min=100.0,
                hysteresis_buffer=2.0,
                is_active=True,
            )
        ]
    return rules


@router.post("/rules", response_model=ThresholdRuleResponse, status_code=status.HTTP_201_CREATED)
def create_threshold_rule(payload: ThresholdRuleCreate, db: Session = Depends(get_db)):
    """Creates a custom threshold rule."""
    rule = ThresholdRule(
        tenant_id="tenant-default-001",
        name=payload.name,
        metric_name=payload.metric_name,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        operator=payload.operator,
        green_max=payload.green_max,
        amber_max=payload.amber_max,
        orange_max=payload.orange_max,
        red_min=payload.red_min,
        hysteresis_buffer=payload.hysteresis_buffer,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/evaluate")
def evaluate_value(
    value: float,
    previous_state: str = "GREEN",
    hysteresis: float = 2.0
):
    """Simulates threshold evaluation and returns resulting color state."""
    state = ThresholdEngine.evaluate_state(
        value=value,
        previous_state=previous_state,
        hysteresis_buffer=hysteresis,
    )
    return {
        "value": value,
        "previous_state": previous_state,
        "evaluated_state": state,
        "state_label": {
            "GREEN": "Normal (<75%)",
            "AMBER": "Warning (75-90%)",
            "ORANGE": "Near Limit (90-100%)",
            "RED": "Critical Exceeded (>100%)",
            "GREY": "Stale / Unknown",
        }.get(state, state),
    }
