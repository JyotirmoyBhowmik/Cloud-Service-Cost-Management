"""
Budget Engine & Utilization Service
Manages hierarchical budgets and evaluates utilization thresholds per User Request §25.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.budget_threshold import Budget
from app.models.cost import CostRecord
from app.models.alert import Alert


class BudgetService:
    """
    Evaluates current spend against defined budgets and generates breach alerts.
    """

    @staticmethod
    def recalculate_budget_utilization(db: Session, budget_id: str) -> Optional[Budget]:
        """
        Recalculates spend for a specific budget and checks warning/critical limits.
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None

        # Calculate actual current spend associated with scope
        spend_query = db.query(func.coalesce(func.sum(CostRecord.billed_cost), 0.0))
        if budget.scope_type == "GLOBAL":
            pass
        elif budget.scope_type == "PROVIDER":
            spend_query = spend_query.filter(CostRecord.provider == budget.scope_id)
        # Add other scope filters as appropriate

        current_spend = spend_query.scalar() or 0.0
        budget.current_spend = round(current_spend, 2)
        budget.forecasted_spend = round(current_spend * 1.05, 2)
        
        utilization_pct = (current_spend / budget.amount) * 100.0 if budget.amount > 0 else 0.0

        # Trigger alerts if warning or critical threshold is exceeded
        if utilization_pct >= budget.critical_threshold_pct:
            existing_alert = (
                db.query(Alert)
                .filter(Alert.budget_id == budget.id, Alert.status.in_(["OPEN", "ACKNOWLEDGED"]))
                .first()
            )
            if not existing_alert:
                alert = Alert(
                    budget_id=budget.id,
                    alert_type="BUDGET_BREACH",
                    severity="CRITICAL",
                    status="OPEN",
                    title=f"Critical Budget Breach: {budget.name}",
                    message=f"Current spend ${budget.current_spend:,.2f} has reached {utilization_pct:.1f}% of budgeted ${budget.amount:,.2f}.",
                    observed_value=utilization_pct,
                    threshold_value=budget.critical_threshold_pct,
                    unit="%",
                )
                db.add(alert)
        elif utilization_pct >= budget.warning_threshold_pct:
            existing_alert = (
                db.query(Alert)
                .filter(Alert.budget_id == budget.id, Alert.status.in_(["OPEN", "ACKNOWLEDGED"]))
                .first()
            )
            if not existing_alert:
                alert = Alert(
                    budget_id=budget.id,
                    alert_type="BUDGET_WARNING",
                    severity="WARNING",
                    status="OPEN",
                    title=f"Warning: Budget Approaching Limit: {budget.name}",
                    message=f"Current spend ${budget.current_spend:,.2f} is at {utilization_pct:.1f}% of budgeted ${budget.amount:,.2f}.",
                    observed_value=utilization_pct,
                    threshold_value=budget.warning_threshold_pct,
                    unit="%",
                )
                db.add(alert)

        db.commit()
        db.refresh(budget)
        return budget
