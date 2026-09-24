"""
Usage Telemetry & Runtime Schemas
Strict DTOs for consumption and schedule monitoring.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class UsageMetricResponse(BaseModel):
    id: str
    resource_id: str
    metric_name: str
    metric_value: float
    metric_unit: str
    recorded_at: datetime
    source: str

    class Config:
        from_attributes = True


class RuntimeRecordResponse(BaseModel):
    id: str
    resource_id: str
    runtime_profile: str
    is_running: bool
    active_hours_today: float
    active_hours_monthly: float
    expected_hours_monthly: float
    schedule_definition: Dict[str, Any]
    schedule_adherence_pct: float
    drift_hours_detected: float
    last_state_change: Optional[datetime] = None

    class Config:
        from_attributes = True
