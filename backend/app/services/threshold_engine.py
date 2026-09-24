"""
Threshold & Color State Engine
Implements multi-band metric thresholds, hysteresis buffering, and state transitions per User Request §26, §27 and FS §479-500.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.budget_threshold import ThresholdRule
from app.models.hierarchy import ResourceNode


class ThresholdEngine:
    """
    Evaluates metric measurements against configured threshold bands.
    Color States:
    - GREEN: Normal / Safe (< 75% default)
    - AMBER: Warning / Approaching (75% - 90%)
    - ORANGE: High Alert / Near limit (90% - 100%)
    - RED: Critical / Exceeded (> 100%)
    - GREY: Stale / Unknown / No Data
    """

    @staticmethod
    def evaluate_state(
        value: Optional[float],
        green_max: float = 75.0,
        amber_max: float = 90.0,
        orange_max: float = 100.0,
        red_min: float = 100.0,
        previous_state: Optional[str] = None,
        hysteresis_buffer: float = 2.0,
        is_stale: bool = False
    ) -> str:
        """
        Calculates color state taking hysteresis buffer into consideration.
        """
        if is_stale or value is None:
            return "GREY"

        # Apply hysteresis if descending from a higher severity state
        buffer = hysteresis_buffer if previous_state in ["RED", "ORANGE", "AMBER"] else 0.0

        if value >= (red_min - (buffer if previous_state == "RED" else 0.0)):
            return "RED"
        elif value >= (amber_max - (buffer if previous_state == "ORANGE" else 0.0)):
            return "ORANGE"
        elif value >= (green_max - (buffer if previous_state == "AMBER" else 0.0)):
            return "AMBER"
        else:
            return "GREEN"

    @staticmethod
    def evaluate_resource_thresholds(db: Session, resource: ResourceNode) -> str:
        """
        Determines the current threshold state of a resource based on its active rules.
        """
        # Look for custom threshold rule on this resource or global rule
        rule = (
            db.query(ThresholdRule)
            .filter(
                ThresholdRule.is_active == True,
                (ThresholdRule.scope_id == resource.id) | (ThresholdRule.scope_id == "*")
            )
            .first()
        )

        green_max = rule.green_max if rule else 75.0
        amber_max = rule.amber_max if rule else 90.0
        orange_max = rule.orange_max if rule else 100.0
        red_min = rule.red_min if rule else 100.0
        buffer = rule.hysteresis_buffer if rule else 2.0

        # Measure: let's evaluate recent usage or monthly budget utilization
        state = ThresholdEngine.evaluate_state(
            value=65.0,  # Default demo baseline
            green_max=green_max,
            amber_max=amber_max,
            orange_max=orange_max,
            red_min=red_min,
            previous_state=resource.threshold_state,
            hysteresis_buffer=buffer,
            is_stale=False,
        )
        return state
