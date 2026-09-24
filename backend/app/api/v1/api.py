"""
API v1 Master Router
Assembles all domain routers into a single OpenAPI namespace.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.providers import router as providers_router
from app.api.v1.connectors import router as connectors_router
from app.api.v1.hierarchy import router as hierarchy_router
from app.api.v1.services import router as services_router
from app.api.v1.resources import router as resources_router
from app.api.v1.pricing import router as pricing_router
from app.api.v1.costs import router as costs_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.thresholds import router as thresholds_router
from app.api.v1.dependencies import router as dependencies_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.reports import router as reports_router
from app.api.v1.admin import router as admin_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(providers_router)
api_v1_router.include_router(connectors_router)
api_v1_router.include_router(hierarchy_router)
api_v1_router.include_router(services_router)
api_v1_router.include_router(resources_router)
api_v1_router.include_router(pricing_router)
api_v1_router.include_router(costs_router)
api_v1_router.include_router(budgets_router)
api_v1_router.include_router(thresholds_router)
api_v1_router.include_router(dependencies_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(onboarding_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(admin_router)
