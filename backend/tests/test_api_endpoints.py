"""
Integration Tests for REST API Endpoints
Uses FastAPI TestClient to test the complete vertical slice end-to-end.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify system liveness probe."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["demo_mode"] is True


def test_auth_login():
    """Verify login authentication flow."""
    payload = {
        "email": "admin@cloudscope.internal",
        "password": "CloudScope2026!",
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "SUPER_ADMIN"


def test_providers_endpoints():
    """Verify multi-cloud provider estate listing."""
    res = client.get("/api/v1/providers")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) == 4
    codes = [p["provider"] for p in providers]
    assert "AZURE" in codes
    assert "AWS" in codes
    assert "GCP" in codes
    assert "OCI" in codes


def test_hierarchy_tree():
    """Verify native and canonical hierarchy tree."""
    res = client.get("/api/v1/hierarchy/tree")
    assert res.status_code == 200
    tree = res.json()
    assert len(tree) > 0
    # Every root node should have children
    assert "id" in tree[0]
    assert "children" in tree[0]


def test_resources_inventory_and_filters():
    """Verify paginated resource inventory and filtering."""
    res = client.get("/api/v1/resources?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total_count"] > 0
    first_item = data["items"][0]
    assert "cost_snapshot" in first_item


def test_resource_explanation_endpoint():
    """Verify Information Icon (ⓘ) explanation payload."""
    # Fetch a resource first
    res_list = client.get("/api/v1/resources?page=1&page_size=1")
    items = res_list.json()["items"]
    assert len(items) > 0
    resource_id = items[0]["id"]

    res_exp = client.get(f"/api/v1/resources/{resource_id}/explanation")
    assert res_exp.status_code == 200
    exp = res_exp.json()
    assert "pricing_status" in exp
    assert "status_reason" in exp
    assert "calculation_formula" in exp
    assert len(exp["assumptions_included"]) > 0


def test_cost_summary_kpi():
    """Verify executive cost summary."""
    res = client.get("/api/v1/costs/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_cost"] > 0
    assert "by_provider" in data
    assert "AZURE" in data["by_provider"]
    assert "AWS" in data["by_provider"]


def test_what_if_simulation_api():
    """Verify What-If calculator endpoint."""
    payload = {
        "provider": "AWS",
        "service_code": "AmazonEC2",
        "region": "us-east-1",
        "quantity": 3,
        "runtime_hours_per_day": 24.0,
        "days_per_month": 30,
        "storage_gb": 200.0,
        "network_egress_gb": 100.0,
    }
    res = client.post("/api/v1/pricing/what-if", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["monthly_cost"] > 0
    assert "formula_explanation" in data


def test_dependencies_graph():
    """Verify topology graph and cost roll-up."""
    res = client.get("/api/v1/dependencies/graph")
    assert res.status_code == 200
    graph = res.json()
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0
    assert graph["total_graph_cost"] > 0


def test_alerts_lifecycle():
    """Verify alert listing and status transition."""
    res = client.get("/api/v1/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) > 0
    
    # Transition first alert to ACKNOWLEDGED
    alert_id = alerts[0]["id"]
    put_res = client.put(f"/api/v1/alerts/{alert_id}/status", json={"status": "ACKNOWLEDGED"})
    assert put_res.status_code == 200
    assert put_res.json()["status"] == "ACKNOWLEDGED"


def test_onboarding_wizard_step():
    """Verify 16-step onboarding wizard validation."""
    payload = {
        "provider": "AZURE",
        "auth_method": "SERVICE_PRINCIPAL",
        "connection_info": {"tenant_id": "demo", "client_id": "demo"},
        "step_number": 4,
    }
    res = client.post("/api/v1/onboarding/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["step_number"] == 4
    assert data["next_step"] == 5


def test_reports_csv_download():
    """Verify CSV streamed reports download."""
    res = client.get("/api/v1/reports/costs.csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Resource Name" in res.text
