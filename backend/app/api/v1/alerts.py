"""
Alert Governance & Lifecycle API
Implements alert lifecycle management (Created -> Open -> Acknowledged -> Resolved) per User Request §33.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, AlertStatusUpdate

router = APIRouter(prefix="/alerts", tags=["Alerts & Governance"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = Query(None, description="OPEN, ACKNOWLEDGED, RESOLVED"),
    severity: Optional[str] = Query(None, description="INFO, WARNING, CRITICAL"),
    db: Session = Depends(get_db)
):
    """Lists alerts filtered by lifecycle status or severity level."""
    query = db.query(Alert).filter(Alert.is_deleted == False)
    if status and status != "ALL":
        query = query.filter(Alert.status == status.upper())
    if severity and severity != "ALL":
        query = query.filter(Alert.severity == severity.upper())
    
    return query.order_by(Alert.created_at.desc()).all()


@router.put("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(alert_id: str, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    """Transitions an alert through its lifecycle states: OPEN -> ACKNOWLEDGED -> RESOLVED."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted == False).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    alert.status = payload.status
    now = datetime.now(timezone.utc)

    if payload.status == "ACKNOWLEDGED":
        alert.acknowledged_by = "admin@cloudscope.internal"
        alert.acknowledged_at = now
    elif payload.status == "RESOLVED":
        alert.resolved_by = "admin@cloudscope.internal"
        alert.resolved_at = now
        alert.resolution_notes = payload.resolution_notes or "Resolved by FinOps administrator."

    db.commit()
    db.refresh(alert)
    return alert
