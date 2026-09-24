"""
Pricing Intelligence Engine
Implements rate evaluation, pricing status classification, and ⓘ explanation generator per User Request §3, §4, §5, §52.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.hierarchy import ResourceNode
from app.models.service_pricing import Service, PricingSKU, PricingTier
from app.schemas.service_pricing import PricingExplanationResponse


class PricingEngine:
    """
    Core pricing engine evaluating whether a service is Free, Free-Tier, Conditional-Free, or Paid,
    and explaining exactly why it costs that amount.
    """

    @staticmethod
    def evaluate_pricing_status(sku: Optional[PricingSKU], usage_units: float = 0.0) -> tuple[str, str]:
        """
        Determines the pricing status and explanation text for a resource/SKU.
        Statuses:
        - FREE: Naturally zero-cost service (e.g. Azure Resource Groups, AWS IAM, GCP VPC peering)
        - FREE_TIER: Included in always-free or 12-month free tier allowance
        - CONDITIONAL_FREE: Free up to allowance limit; chargeable after
        - PAID: Standard chargeable service
        - ESTIMATED: Cost calculated using list price and estimated usage
        - UNKNOWN: Missing SKU or catalog data
        - NOT_APPLICABLE: Grouping or container node
        """
        if not sku:
            return "UNKNOWN", "No matching pricing SKU or catalog rate could be resolved."

        if sku.is_free:
            return "FREE", "No direct provider charge for this core management service."

        if sku.free_allowance_units > 0:
            if usage_units <= sku.free_allowance_units:
                return (
                    "FREE_TIER",
                    f"Free within included provider allowance ({sku.free_allowance_units} {sku.billing_unit}); "
                    f"charges apply after exceeding this tier."
                )
            else:
                return (
                    "CONDITIONAL_FREE",
                    f"Current usage ({usage_units} {sku.billing_unit}) exceeds free tier allowance of "
                    f"{sku.free_allowance_units} {sku.billing_unit}; incremental usage is billed at ${sku.unit_price}."
                )

        if sku.unit_price > 0:
            return "PAID", f"Chargeable on-demand service at standard catalog rate of ${sku.unit_price} per {sku.billing_unit}."

        return "UNKNOWN", "Pricing parameters are not fully defined in the catalog."

    @staticmethod
    def calculate_cost_from_sku(
        sku: PricingSKU,
        quantity: float,
        tiers: Optional[List[PricingTier]] = None
    ) -> float:
        """
        Calculates total cost using flat or tiered pricing models.
        """
        if not sku or quantity <= 0:
            return 0.0

        billable_quantity = max(0.0, quantity - sku.free_allowance_units)
        if billable_quantity <= 0:
            return 0.0

        # Tiered pricing calculation
        if sku.pricing_model == "TIERED" and tiers:
            total_cost = 0.0
            remaining_qty = billable_quantity
            sorted_tiers = sorted(tiers, key=lambda t: t.start_amount)

            for tier in sorted_tiers:
                tier_cap = tier.end_amount if tier.end_amount is not None else float("inf")
                tier_span = tier_cap - tier.start_amount
                
                if remaining_qty > 0:
                    qty_in_tier = min(remaining_qty, tier_span)
                    total_cost += qty_in_tier * tier.unit_price
                    remaining_qty -= qty_in_tier
                else:
                    break
            return round(total_cost, 4)

        # Standard flat rate
        return round(billable_quantity * sku.unit_price, 4)

    @staticmethod
    def get_pricing_explanation(
        db: Session,
        resource: ResourceNode
    ) -> PricingExplanationResponse:
        """
        Generates the comprehensive data contract for the ⓘ Information Icon modal/tooltip.
        Answers: 'Why does this service cost this amount?'
        """
        service_name = resource.service.service_name if resource.service else resource.native_type
        service_family = resource.service.service_family if resource.service else "Cloud Infrastructure"
        
        # Resolve SKU
        sku = None
        if resource.service and resource.service.skus:
            # Match region if available
            matching_skus = [s for s in resource.service.skus if s.region == resource.region]
            sku = matching_skus[0] if matching_skus else resource.service.skus[0]

        monthly_hours = 720.0  # Standard 30 days * 24 hours
        status, reason = PricingEngine.evaluate_pricing_status(sku, monthly_hours)

        unit_price = sku.unit_price if sku else 0.0
        billing_unit = sku.billing_unit if sku else "1 Hour"
        currency = sku.currency if sku else "USD"
        pricing_model = sku.pricing_model if sku else "PER_HOUR"
        pricing_source = sku.pricing_source if sku else "ESTIMATED_DEFAULT"
        sku_id = sku.provider_sku_id if sku else "N/A"
        sku_name = sku.sku_name if sku else f"{resource.native_type} Default Rate"

        # Calculate monthly cost
        monthly_cost = PricingEngine.calculate_cost_from_sku(
            sku=sku,
            quantity=monthly_hours,
            tiers=sku.tiers if sku else None
        ) if sku else 0.0

        # Construct formula text
        if not sku or sku.is_free:
            formula = "$0.00 (Core zero-rated resource)"
        elif sku.free_allowance_units > 0:
            formula = (
                f"({monthly_hours} {billing_unit} - {sku.free_allowance_units} free allowance) "
                f"× ${unit_price}/{billing_unit} = ${monthly_cost:.2f}"
            )
        else:
            formula = f"{monthly_hours} {billing_unit} × ${unit_price:.4f}/{billing_unit} = ${monthly_cost:.2f}"

        assumptions_inc = [
            "Continuous 24x7 runtime (720 hours / 30 calendar days)",
            f"Official list price rate for region '{resource.region or 'global'}'",
            "On-Demand pay-as-you-go commercial baseline",
        ]
        
        assumptions_exc = [
            "Data transfer / internet egress fees (metered separately)",
            "Snapshot / backup storage attachments",
            "Premium OS licensing surcharges",
            "Applicable enterprise agreement discounts or committed use credits",
        ]

        return PricingExplanationResponse(
            resource_id=resource.id,
            resource_name=resource.name,
            provider=resource.provider,
            service_name=service_name,
            service_family=service_family,
            pricing_status=status,
            status_reason=reason,
            provider_sku_id=sku_id,
            sku_name=sku_name,
            billing_unit=billing_unit,
            unit_price=unit_price,
            currency=currency,
            pricing_model=pricing_model,
            region=resource.region,
            free_allowance=f"{sku.free_allowance_units} {billing_unit} / month" if sku and sku.free_allowance_units > 0 else None,
            commitment_discount="0% (On-Demand catalog price)",
            usage_quantity=monthly_hours,
            usage_unit="Hours",
            monthly_cost=monthly_cost,
            cost_calculation_method="Standard Rate × Runtime Quantity",
            calculation_formula=formula,
            assumptions_included=assumptions_inc,
            assumptions_excluded=assumptions_exc,
            pricing_source=pricing_source,
            effective_date="2026-09-01",
            retrieval_timestamp=datetime.now(timezone.utc),
        )
