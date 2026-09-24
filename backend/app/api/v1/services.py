"""
Service Catalog Endpoints
Provides cloud service inventory and SKU rate lists per User Request §20.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service_pricing import Service, PricingSKU
from app.models.hierarchy import ResourceNode
from app.schemas.service_pricing import ServiceResponse, PricingSKUResponse

router = APIRouter(prefix="/services", tags=["Service Catalog"])


@router.get("", response_model=List[ServiceResponse])
def list_services(
    provider: Optional[str] = Query(None, description="Optional provider filter (AZURE, AWS, GCP, OCI)"),
    family: Optional[str] = Query(None, description="Optional service family filter (Compute, Storage, Database, Network)"),
    db: Session = Depends(get_db)
):
    """Lists registered cloud services with associated rate SKUs and resource counts."""
    query = db.query(Service).filter(Service.is_deleted == False)
    if provider and provider != "ALL":
        query = query.filter(Service.provider == provider.upper())
    if family:
        query = query.filter(Service.service_family == family)

    services = query.all()
    results = []
    for s in services:
        res_count = db.query(ResourceNode).filter(ResourceNode.service_id == s.id, ResourceNode.is_deleted == False).count()
        dto = ServiceResponse.model_validate(s)
        dto.resource_count = res_count
        results.append(dto)
    return results


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service_detail(service_id: str, db: Session = Depends(get_db)):
    """Retrieves full metadata and SKUs for a specific cloud service."""
    service = db.query(Service).filter(Service.id == service_id, Service.is_deleted == False).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")
    res_count = db.query(ResourceNode).filter(ResourceNode.service_id == service.id, ResourceNode.is_deleted == False).count()
    dto = ServiceResponse.model_validate(service)
    dto.resource_count = res_count
    return dto
