"""
Dependency & Topology Engine
Implements service relationship graphs and cost-aware dependency chains per User Request §30, §31, §32.
"""

from typing import List, Dict, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.hierarchy import ResourceNode
from app.models.dependency import DependencyEdge
from app.models.cost import CostRecord
from app.schemas.dependency import DependencyGraphResponse, DependencyNodeDTO, DependencyEdgeDTO


class DependencyEngine:
    """
    Constructs topological service dependency trees and computes cumulative application costs:
    Direct Cost + Dependent Costs = Total Application Cost.
    """

    @staticmethod
    def get_topology_graph(db: Session, filter_provider: str = None) -> DependencyGraphResponse:
        """
        Builds graph payload with calculated direct and downstream dependent costs.
        """
        query = db.query(ResourceNode).filter(ResourceNode.canonical_role == "RESOURCE")
        if filter_provider and filter_provider != "ALL":
            query = query.filter(ResourceNode.provider == filter_provider)
        resources = query.all()

        # Map resource_id -> direct monthly cost
        cost_map: Dict[str, float] = {}
        for r in resources:
            cost_row = (
                db.query(func.coalesce(func.sum(CostRecord.billed_cost), 0.0))
                .filter(CostRecord.resource_id == r.id)
                .scalar() or 0.0
            )
            cost_map[r.id] = round(cost_row, 2)

        # Query all edges
        edge_records = db.query(DependencyEdge).all()
        edges_dto: List[DependencyEdgeDTO] = []
        
        # Build adjacency for downstream traversal: target depends on source, or source depends on target
        # For DEPENDS_ON: Target depends on Source (e.g. WebApp DEPENDS_ON Database)
        child_map: Dict[str, List[Tuple[str, float]]] = {}
        for edge in edge_records:
            edges_dto.append(
                DependencyEdgeDTO(
                    id=edge.id,
                    source_id=edge.source_node_id,
                    target_id=edge.target_node_id,
                    edge_type=edge.edge_type,
                    confidence_score=edge.confidence_score,
                    cost_allocation_pct=edge.cost_allocation_pct,
                )
            )
            child_map.setdefault(edge.source_node_id, []).append((edge.target_node_id, edge.cost_allocation_pct / 100.0))

        # Calculate dependent and total cost for each node
        nodes_dto: List[DependencyNodeDTO] = []
        total_graph_cost = 0.0

        for r in resources:
            direct = cost_map.get(r.id, 0.0)
            
            # Traverse dependents (depth-first search with visited set to prevent cycles)
            visited: Set[str] = set()
            dependent_cost = 0.0
            queue = [(dep_id, weight) for dep_id, weight in child_map.get(r.id, [])]

            while queue:
                current_id, weight = queue.pop(0)
                if current_id in visited:
                    continue
                visited.add(current_id)
                dep_direct = cost_map.get(current_id, 0.0)
                dependent_cost += dep_direct * weight
                for next_id, next_weight in child_map.get(current_id, []):
                    if next_id not in visited:
                        queue.append((next_id, weight * next_weight))

            total_cost = round(direct + dependent_cost, 2)
            total_graph_cost += direct

            service_name = r.service.service_name if r.service else r.native_type
            service_family = r.service.service_family if r.service else "Compute"

            nodes_dto.append(
                DependencyNodeDTO(
                    id=r.id,
                    canonical_id=r.canonical_id,
                    name=r.name,
                    provider=r.provider,
                    service_name=service_name,
                    service_family=service_family,
                    environment=r.environment,
                    direct_cost=direct,
                    dependent_cost=round(dependent_cost, 2),
                    total_cost=total_cost,
                    currency="USD",
                    threshold_state=r.threshold_state,
                    pricing_status=r.pricing_status,
                )
            )

        return DependencyGraphResponse(
            nodes=nodes_dto,
            edges=edges_dto,
            total_graph_cost=round(total_graph_cost, 2),
            currency="USD",
            cluster_count=len(set(r.provider for r in resources)),
        )
