"""
Reporting & Data Export Engine
Generates CSV and tabular reports for Costs, Budgets, and Services per User Request §42.
"""

import io
import csv
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.hierarchy import ResourceNode
from app.models.cost import CostRecord
from app.models.budget_threshold import Budget
from app.models.alert import Alert


class ReportService:
    """
    Generates downloadable reports in CSV format.
    """

    @staticmethod
    def generate_cost_report_csv(db: Session) -> str:
        """Generates full cost detail report as CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "Resource Name", "Provider", "Region", "Environment", "Business Unit",
            "Service", "Cost State", "Billed Cost ($)", "Effective Cost ($)",
            "Usage Quantity", "Usage Unit", "Period Start", "Period End"
        ])

        records = (
            db.query(CostRecord, ResourceNode)
            .join(ResourceNode, ResourceNode.id == CostRecord.resource_id)
            .order_by(CostRecord.billed_cost.desc())
            .all()
        )

        for cost, res in records:
            service_name = res.service.service_name if res.service else res.native_type
            writer.writerow([
                res.name,
                cost.provider,
                res.region or "Global",
                res.environment,
                res.business_unit or "N/A",
                service_name,
                cost.cost_state,
                f"{cost.billed_cost:.2f}",
                f"{cost.effective_cost:.2f}",
                cost.usage_quantity,
                cost.usage_unit,
                cost.period_start.strftime("%Y-%m-%d"),
                cost.period_end.strftime("%Y-%m-%d"),
            ])

        return output.getvalue()

    @staticmethod
    def generate_budget_report_csv(db: Session) -> str:
        """Generates budget utilization report as CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "Budget Name", "Scope Type", "Scope ID", "Budgeted Amount ($)",
            "Current Spend ($)", "Utilization (%)", "Warning Threshold (%)",
            "Critical Threshold (%)", "Status"
        ])

        budgets = db.query(Budget).all()
        for b in budgets:
            utilization = (b.current_spend / b.amount) * 100.0 if b.amount > 0 else 0.0
            status = "CRITICAL" if utilization >= b.critical_threshold_pct else "WARNING" if utilization >= b.warning_threshold_pct else "NORMAL"
            writer.writerow([
                b.name,
                b.scope_type,
                b.scope_id,
                f"{b.amount:.2f}",
                f"{b.current_spend:.2f}",
                f"{utilization:.1f}",
                f"{b.warning_threshold_pct:.1f}",
                f"{b.critical_threshold_pct:.1f}",
                status,
            ])

        return output.getvalue()
