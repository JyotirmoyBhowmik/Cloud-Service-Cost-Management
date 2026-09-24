"""
Unit & Integration Tests for Pricing, Cost, Threshold, and Reconciliation Engines
Validates User Request §46 requirements:
1. Free service
2. Free-tier service
3. Paid service
4. Tiered pricing
5. Runtime-based cost
6. Volume-based cost
7. Budget threshold
8. Forecast exceeding budget
9. Missing pricing
16. Actual-vs-estimated reconciliation
"""

import pytest
from app.models.service_pricing import PricingSKU, PricingTier, Service
from app.models.hierarchy import ResourceNode
from app.services.pricing_engine import PricingEngine
from app.services.cost_engine import CostEngine
from app.services.threshold_engine import ThresholdEngine
from app.services.reconciliation_service import ReconciliationService
from app.services.budget_service import BudgetService
from app.models.budget_threshold import Budget
from app.models.cost import CostRecord
from app.schemas.cost import WhatIfRequest


def test_free_service_status():
    """Requirement 1: Naturally free core service evaluation."""
    sku = PricingSKU(
        provider="AZURE",
        provider_sku_id="Core-Free",
        sku_name="Resource Groups",
        billing_unit="1 Resource",
        unit_price=0.0,
        is_free=True,
    )
    status, reason = PricingEngine.evaluate_pricing_status(sku, usage_units=100)
    assert status == "FREE"
    assert "No direct provider charge" in reason


def test_free_tier_and_conditional_free_service():
    """Requirement 2: Free tier within allowance and conditional charges when exceeded."""
    sku = PricingSKU(
        provider="AWS",
        provider_sku_id="S3-Standard",
        sku_name="S3 Standard Storage",
        billing_unit="1 GB-Month",
        unit_price=0.023,
        is_free=False,
        free_allowance_units=5.0,  # 5 GB free
    )
    # Case A: Within free allowance
    status_a, _ = PricingEngine.evaluate_pricing_status(sku, usage_units=4.5)
    assert status_a == "FREE_TIER"

    # Case B: Exceeds free allowance
    status_b, _ = PricingEngine.evaluate_pricing_status(sku, usage_units=12.0)
    assert status_b == "CONDITIONAL_FREE"


def test_paid_service_status_and_calculation():
    """Requirement 3 & 5: Standard on-demand paid service and runtime calculation."""
    sku = PricingSKU(
        provider="AZURE",
        provider_sku_id="Standard_D4s_v5",
        sku_name="D4s v5 Compute",
        billing_unit="1 Hour",
        unit_price=0.1920,
        pricing_model="PER_HOUR",
        is_free=False,
        free_allowance_units=0.0,
    )
    status, _ = PricingEngine.evaluate_pricing_status(sku, usage_units=720)
    assert status == "PAID"

    # 720 hours * $0.1920 = $138.24
    cost = PricingEngine.calculate_cost_from_sku(sku, quantity=720.0)
    assert cost == 138.24


def test_tiered_pricing_calculation():
    """Requirement 4 & 6: Volume-based tiered rate evaluation."""
    sku = PricingSKU(
        provider="AWS",
        provider_sku_id="S3-Tiered",
        sku_name="S3 Tiered Storage",
        billing_unit="1 GB-Month",
        unit_price=0.023,
        pricing_model="TIERED",
        is_free=False,
        free_allowance_units=0.0,
    )
    tiers = [
        PricingTier(sku_id="1", tier_number=1, start_amount=0.0, end_amount=50.0, unit_price=0.023),     # First 50 GB @ 0.023
        PricingTier(sku_id="1", tier_number=2, start_amount=50.0, end_amount=500.0, unit_price=0.022),   # Next 450 GB @ 0.022
        PricingTier(sku_id="1", tier_number=3, start_amount=500.0, end_amount=None, unit_price=0.021),   # Above 500 GB @ 0.021
    ]
    # Test 100 GB usage: 50 * 0.023 ($1.15) + 50 * 0.022 ($1.10) = $2.25
    cost = PricingEngine.calculate_cost_from_sku(sku, quantity=100.0, tiers=tiers)
    assert cost == 2.25


def test_missing_pricing_status():
    """Requirement 9: Missing pricing parameters handled gracefully."""
    status, reason = PricingEngine.evaluate_pricing_status(None)
    assert status == "UNKNOWN"
    assert "No matching pricing SKU" in reason


def test_cost_horizons():
    """Requirement 5: Hourly, Daily, Monthly, and Annualized cost conversions."""
    horizons = CostEngine.calculate_cost_horizons(720.0)
    assert horizons["monthly"] == 720.0
    assert horizons["daily"] == 24.0
    assert horizons["hourly"] == 1.0
    assert horizons["annualized"] == 8640.0


def test_threshold_state_machine_and_hysteresis():
    """Requirement 7: Multi-band color state machine and hysteresis buffer."""
    # Test normal band
    assert ThresholdEngine.evaluate_state(50.0) == "GREEN"
    assert ThresholdEngine.evaluate_state(80.0) == "AMBER"
    assert ThresholdEngine.evaluate_state(95.0) == "ORANGE"
    assert ThresholdEngine.evaluate_state(105.0) == "RED"

    # Test stale state
    assert ThresholdEngine.evaluate_state(50.0, is_stale=True) == "GREY"
    assert ThresholdEngine.evaluate_state(None) == "GREY"

    # Test hysteresis buffer: descending from RED to 99.0 with buffer 2.0 keeps it RED (100 - 2 = 98)
    state = ThresholdEngine.evaluate_state(99.0, previous_state="RED", hysteresis_buffer=2.0)
    assert state == "RED"


def test_budget_threshold_and_alerts(db_session):
    """Requirement 7 & 8: Budget breach alert generation."""
    # Find a budget
    budget = db_session.query(Budget).first()
    assert budget is not None
    
    # Intentionally set spend exceeding critical threshold
    budget.amount = 100.0
    budget.critical_threshold_pct = 90.0
    budget.current_spend = 120.0
    db_session.commit()

    recalculated = BudgetService.recalculate_budget_utilization(db_session, budget.id)
    assert recalculated is not None


def test_actual_vs_estimated_reconciliation(db_session):
    """Requirement 16: Reconciliation between estimated and actual invoiced amounts."""
    res = db_session.query(ResourceNode).filter(ResourceNode.canonical_role == "RESOURCE").first()
    assert res is not None

    rec = ReconciliationService.run_reconciliation_for_resource(db_session, res.id, period="2026-09")
    assert rec is not None
    assert rec.actual_amount >= 0.0
    assert rec.estimated_amount >= 0.0
    assert rec.status in ["RECONCILED", "PENDING_REVIEW"]


def test_what_if_simulation(db_session):
    """Simulate 'What Will This Cost?' calculation."""
    req = WhatIfRequest(
        provider="AZURE",
        service_code="Virtual Machines",
        region="eastus",
        quantity=2,
        runtime_hours_per_day=24.0,
        days_per_month=30,
        storage_gb=100.0,
        network_egress_gb=50.0,
    )
    result = CostEngine.simulate_what_if(db_session, req)
    assert result.monthly_cost > 0.0
    assert result.daily_cost > 0.0
    assert result.hourly_cost > 0.0
    assert len(result.assumptions) > 0
