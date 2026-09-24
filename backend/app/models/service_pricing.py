"""
Service Catalog & Pricing SKU Models
Represents cloud service taxonomy and pricing catalogs per BBP §361-423 and FS §1035-1070.
"""

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, JSON, DateTime, Text, Index
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid


class Service(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "services"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider = Column(String(20), nullable=False, index=True)  # AZURE, AWS, GCP, OCI
    service_code = Column(String(100), nullable=False, index=True)  # Virtual Machines, AmazonEC2, Compute Engine, Compute
    service_name = Column(String(150), nullable=False)
    service_family = Column(String(100), nullable=False, index=True)  # Compute, Storage, Database, Network, AI, Analytics
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    default_pricing_model = Column(String(50), default="PER_HOUR")
    has_free_tier = Column(Boolean, default=False)
    free_tier_description = Column(Text, nullable=True)

    resources = relationship("ResourceNode", back_populates="service")
    skus = relationship("PricingSKU", back_populates="service", cascade="all, delete-orphan")


class PricingSKU(Base, TimestampMixin):
    __tablename__ = "pricing_skus"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    service_id = Column(String(36), ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False, index=True)
    provider_sku_id = Column(String(255), nullable=False, index=True)  # D2s_v5, t3.medium, e2-standard-2, VM.Standard.E4.Flex
    sku_name = Column(String(255), nullable=False)
    meter_name = Column(String(150), nullable=True)
    
    # Financial units & pricing
    pricing_model = Column(String(50), default="PER_HOUR", nullable=False)  # PER_HOUR, PER_GB_MONTH, PER_REQUEST, TIERED, FLAT
    billing_unit = Column(String(50), nullable=False)  # 1 Hour, 1 GB-Month, 10,000 Requests
    unit_price = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    region = Column(String(50), nullable=False, index=True)
    
    # Free tier & conditional allowances
    is_free = Column(Boolean, default=False)
    free_allowance_units = Column(Float, default=0.0)  # e.g. 750 hours free per month
    free_allowance_description = Column(Text, nullable=True)
    
    # Commitment & effective dates
    commitment_type = Column(String(50), default="ON_DEMAND")  # ON_DEMAND, 1_YEAR_RESERVATION, 3_YEAR_RESERVATION, SPOT
    effective_start = Column(DateTime, nullable=True)
    effective_end = Column(DateTime, nullable=True)
    pricing_source = Column(String(100), default="API_CATALOG")  # RETAIL_PRICES_API, PRICE_LIST_API, BILLING_CATALOG
    raw_pricing_metadata = Column(JSON, default=dict)

    service = relationship("Service", back_populates="skus")
    tiers = relationship("PricingTier", back_populates="sku", cascade="all, delete-orphan")
    cost_records = relationship("CostRecord", back_populates="sku")

    __table_args__ = (
        Index("ix_pricingsku_provider_sku_region", "provider", "provider_sku_id", "region"),
    )


class PricingTier(Base, TimestampMixin):
    __tablename__ = "pricing_tiers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sku_id = Column(String(36), ForeignKey("pricing_skus.id", ondelete="CASCADE"), nullable=False, index=True)
    tier_number = Column(Float, nullable=False)
    start_amount = Column(Float, default=0.0, nullable=False)
    end_amount = Column(Float, nullable=True)  # None = infinity / above
    unit_price = Column(Float, nullable=False)

    sku = relationship("PricingSKU", back_populates="tiers")
