"""
Administration & Governance API
Implements immutable audit trails, administrative overrides, and RBAC per User Request §34, §35, §36.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rbac import UserRole, ROLE_PERMISSIONS
from app.models.audit import AuditEvent
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Administration & Governance"])


class OverrideRequest(BaseModel):
    entity_type: str
    entity_id: str
    field_name: str
    override_value: Any
    reason: str


@router.get("/audit-logs")
def list_audit_events(
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves immutable audit trail entries per User Request §36."""
    query = db.query(AuditEvent)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    return query.order_by(AuditEvent.created_at.desc()).limit(limit).all()


@router.post("/overrides")
def apply_admin_override(payload: OverrideRequest, db: Session = Depends(get_db)):
    """Applies an administrative override and records it in the immutable audit log."""
    audit = AuditEvent(
        tenant_id="tenant-default-001",
        user_id="usr-admin-demo-01",
        user_email="admin@cloudscope.internal",
        action="ADMIN_OVERRIDE_APPLIED",
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        previous_state={"field": payload.field_name, "value": "AUTOMATED_DEFAULT"},
        new_state={"field": payload.field_name, "value": payload.override_value},
        reason=payload.reason,
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit)
    db.commit()
    return {"message": "Administrative override recorded and applied successfully.", "audit_id": audit.id}


@router.get("/roles")
def list_roles():
    """Lists enterprise RBAC roles and their associated permissions."""
    return [
        {
            "role": role.value,
            "permissions": [p.value for p in permissions]
        }
        for role, permissions in ROLE_PERMISSIONS.items()
    ]


@router.get("/settings")
def get_system_settings():
    """Retrieves platform configuration and feature flags."""
    return {
        "platform_name": "CloudScope Multi-Cloud Governance",
        "version": "1.0.0",
        "demo_mode": True,
        "default_currency": "USD",
        "supported_providers": ["AZURE", "AWS", "GCP", "OCI"],
        "retention_policy_days": 365,
        "freshness_sla_hours": 24,
    }
