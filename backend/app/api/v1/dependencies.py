"""
Topology & Dependency Graph API
Implements interactive service topology graph and cost-aware chains per User Request §30, §31, §32.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dependency import DependencyEdge
from app.schemas.dependency import DependencyGraphResponse, DependencyEdgeCreate, DependencyEdgeDTO
from app.services.dependency_engine import DependencyEngine

router = APIRouter(prefix="/dependencies", tags=["Service Dependencies & Topology"])


@router.get("/graph", response_model=DependencyGraphResponse)
def get_dependency_graph(
    provider: Optional[str] = Query(None, description="Optional provider filter (AZURE, AWS, GCP, OCI)"),
    db: Session = Depends(get_db)
):
    """
    Returns nodes and edges for the interactive topology graph.
    Computes Direct Cost + Dependent Cost = Total Application Cost for every node.
    """
    return DependencyEngine.get_topology_graph(db, filter_provider=provider)


@router.post("/edges", status_code=status.HTTP_201_CREATED)
def create_dependency_edge(payload: DependencyEdgeCreate, db: Session = Depends(get_db)):
    """Creates a directed dependency edge between two services."""
    edge = DependencyEdge(
        source_node_id=payload.source_node_id,
        target_node_id=payload.target_node_id,
        edge_type=payload.edge_type,
        confidence_score=payload.confidence_score,
        cost_allocation_pct=payload.cost_allocation_pct,
        source_type="MANUAL_OVERLAY",
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return {"id": edge.id, "message": "Dependency edge established successfully."}
