"""
Hierarchy Explorer API Endpoints
Constructs recursive trees representing native and canonical cloud structures per User Request §9.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.hierarchy import ResourceNode
from app.models.cost import CostRecord
from app.schemas.hierarchy import HierarchyTreeNode, HierarchySummaryResponse

router = APIRouter(prefix="/hierarchy", tags=["Hierarchy Explorer"])


def build_tree_recursive(node: ResourceNode, cost_map: Dict[str, float]) -> HierarchyTreeNode:
    """Recursively constructs hierarchy node tree."""
    direct_cost = cost_map.get(node.id, 0.0)
    children_trees = [build_tree_recursive(c, cost_map) for c in node.children if not c.is_deleted]
    
    # Total monthly cost rolls up children
    child_sum = sum(c.monthly_cost for c in children_trees)
    total_cost = round(direct_cost + child_sum, 2)
    resource_count = (1 if node.canonical_role == "RESOURCE" else 0) + sum(c.resource_count for c in children_trees)

    return HierarchyTreeNode(
        id=node.id,
        canonical_id=node.canonical_id,
        name=node.name,
        provider=node.provider,
        native_type=node.native_type,
        canonical_role=node.canonical_role,
        region=node.region,
        environment=node.environment,
        pricing_status=node.pricing_status,
        threshold_state=node.threshold_state,
        monthly_cost=total_cost,
        currency="USD",
        resource_count=resource_count,
        children=children_trees,
    )


@router.get("/tree", response_model=List[HierarchyTreeNode])
def get_hierarchy_tree(
    provider: Optional[str] = Query(None, description="Optional provider filter (AZURE, AWS, GCP, OCI)"),
    db: Session = Depends(get_db)
):
    """
    Returns full hierarchy tree starting from Root Governance nodes down to individual billable resources.
    Preserves native hierarchies (Azure Management Groups, AWS OUs, GCP Folders, OCI Compartments).
    """
    # Fetch all resource direct costs
    cost_rows = (
        db.query(CostRecord.resource_id, func.sum(CostRecord.billed_cost))
        .group_by(CostRecord.resource_id)
        .all()
    )
    cost_map = {res_id: float(cost) for res_id, cost in cost_rows}

    # Query root nodes (parent_id is None)
    query = db.query(ResourceNode).filter(ResourceNode.parent_id == None, ResourceNode.is_deleted == False)
    if provider and provider != "ALL":
        query = query.filter(ResourceNode.provider == provider.upper())
    
    root_nodes = query.all()
    tree = [build_tree_recursive(root, cost_map) for root in root_nodes]
    return tree


@router.get("/summary", response_model=HierarchySummaryResponse)
def get_hierarchy_summary(db: Session = Depends(get_db)):
    """Provides high-level distribution counts across roles, environments, and cloud providers."""
    nodes = db.query(ResourceNode).filter(ResourceNode.is_deleted == False).all()
    total_spend = db.query(func.coalesce(func.sum(CostRecord.billed_cost), 0.0)).scalar() or 0.0

    by_prov: Dict[str, int] = {}
    by_role: Dict[str, int] = {}
    by_env: Dict[str, int] = {}

    for n in nodes:
        by_prov[n.provider] = by_prov.get(n.provider, 0) + 1
        by_role[n.canonical_role] = by_role.get(n.canonical_role, 0) + 1
        by_env[n.environment] = by_env.get(n.environment, 0) + 1

    return HierarchySummaryResponse(
        total_nodes=len(nodes),
        providers=by_prov,
        by_canonical_role=by_role,
        by_environment=by_env,
        total_monthly_spend=round(total_spend, 2),
        currency="USD",
    )
