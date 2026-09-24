"""
Reports & Data Export API
Streams downloadable CSV reports per User Request §42.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reporting & Exports"])


@router.get("/costs.csv")
def download_cost_report_csv(db: Session = Depends(get_db)):
    """Generates and downloads a CSV export of all resource costs."""
    csv_data = ReportService.generate_cost_report_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cloudscope_costs_report.csv"}
    )


@router.get("/budgets.csv")
def download_budget_report_csv(db: Session = Depends(get_db)):
    """Generates and downloads a CSV export of budget utilizations."""
    csv_data = ReportService.generate_budget_report_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cloudscope_budgets_report.csv"}
    )
