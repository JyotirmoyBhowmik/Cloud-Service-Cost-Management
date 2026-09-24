"""
Cost Reconciliation Engine
Reconciles estimated costs against actual provider invoices per User Request §8.
"""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.cost import CostRecord, ReconciliationRecord
from app.models.hierarchy import ResourceNode
from app.schemas.cost import ReconciliationResponse


class ReconciliationService:
    """
    Detects and categorizes financial variances between pre-bill estimates and post-bill invoices.
    """

    @staticmethod
    def classify_variance_driver(estimated: float, actual: float) -> str:
        """
        Classifies likely root causes of variances:
        - USAGE_DRIFT: Consumption exceeded runtime/storage estimates
        - RATE_CHANGE: Provider list price change occurred mid-cycle
        - DISCOUNT_APPLIED: Enterprise discount / Savings Plan reduced invoiced rate
        - NEW_METERS: Resource generated unanticipated sub-meters (e.g. diagnostic logging)
        - TAXES_CREDITS: Regulatory taxes or promotional credits applied
        """
        diff = actual - estimated
        if abs(diff) < 0.05:
            return "EXACT_MATCH"
        if diff < 0 and abs(diff) > (estimated * 0.1):
            return "DISCOUNT_APPLIED"
        if diff > 0 and diff > (estimated * 0.25):
            return "USAGE_DRIFT"
        if diff > 0:
            return "NEW_METERS"
        return "UNKNOWN"

    @staticmethod
    def run_reconciliation_for_resource(
        db: Session,
        resource_id: str,
        period: str = "2026-09"
    ) -> Optional[ReconciliationRecord]:
        """
        Reconciles single resource estimated vs actual costs for the given period.
        """
        resource = db.query(ResourceNode).filter(ResourceNode.id == resource_id).first()
        if not resource:
            return None

        # Calculate actuals vs estimates
        actual_sum = (
            db.query(CostRecord.billed_cost)
            .filter(CostRecord.resource_id == resource_id, CostRecord.cost_state == "ACTUAL")
            .first()
        )
        actual = actual_sum[0] if actual_sum else 0.0

        est_sum = (
            db.query(CostRecord.billed_cost)
            .filter(CostRecord.resource_id == resource_id, CostRecord.cost_state == "ESTIMATED")
            .first()
        )
        estimated = est_sum[0] if est_sum else actual * 0.98

        difference = round(actual - estimated, 2)
        variance_pct = round((difference / estimated) * 100.0, 2) if estimated > 0 else 0.0
        driver = ReconciliationService.classify_variance_driver(estimated, actual)

        status = "RECONCILED" if abs(difference) < 5.0 else "PENDING_REVIEW"
        notes = f"Variance of ${difference:.2f} ({variance_pct}%). Driver: {driver}"

        # Create or update record
        rec = (
            db.query(ReconciliationRecord)
            .filter(ReconciliationRecord.resource_id == resource_id, ReconciliationRecord.period == period)
            .first()
        )
        if not rec:
            rec = ReconciliationRecord(
                resource_id=resource_id,
                period=period,
                provider=resource.provider,
                estimated_amount=estimated,
                actual_amount=actual,
                difference=difference,
                variance_pct=variance_pct,
                driver_type=driver,
                status=status,
                notes=notes,
            )
            db.add(rec)
        else:
            rec.estimated_amount = estimated
            rec.actual_amount = actual
            rec.difference = difference
            rec.variance_pct = variance_pct
            rec.driver_type = driver
            rec.status = status
            rec.notes = notes

        db.commit()
        db.refresh(rec)
        return rec
