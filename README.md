# CloudScope: Enterprise Multi-Cloud Service Inventory & Cost Governance Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com)
[![FOCUS](https://img.shields.io/badge/FinOps-FOCUS_1.4-green.svg)](https://focus.finops.org)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

CloudScope is a production-oriented, open-source web application for **Multi-Cloud Service Inventory, Pricing Intelligence, Cost Management, Runtime/Usage Monitoring, Budgeting, Multi-Band Thresholds, Dependency Mapping, and Governance** across:
- **Microsoft Azure**
- **Amazon Web Services (AWS)**
- **Google Cloud Platform (GCP)**
- **Oracle Cloud Infrastructure (OCI)**

Designed strictly per the **CloudScope Business Blueprint (BBP) and Functional Specification (FS)** and compliant with the **FinOps FOCUS 1.4 specification**.

---

## 1. Key Architectural Principles

1. **Native Cloud Hierarchy Parity:** CloudScope preserves exact provider structures:
   - **Azure:** Tenant → Root Management Group → Management Groups → Subscriptions → Resource Groups → Resources
   - **AWS:** Organization → Organizational Units (OUs) → Accounts → Regions → Resources
   - **GCP:** Organization → Folders → Projects → Regions/Zones → Resources
   - **OCI:** Tenancy → Compartments → Subcompartments → Availability Domains → Resources
   *All wrapped in a canonical abstraction layer (`ResourceNode`) without flattening or distorting native topologies.*
2. **Pricing Intelligence & Transparency:** Distinguishes between `FREE`, `FREE_TIER`, `CONDITIONAL_FREE`, `PAID`, `ESTIMATED`, and `UNKNOWN`. Never presents an estimate as actual billed data.
3. **The Information Icon (ⓘ) — "Why does this service cost this amount?":** Clicking the ⓘ icon throughout the UI renders a deep mathematical calculation trace, unit pricing, formula, billing units, free tier limits, and included/excluded assumptions without leaving the screen.
4. **FOCUS 1.4 Cost Separation & Reconciliation:** Maintains clear separation between Billed Actuals (invoices), Estimated Rates (usage × catalog), and Forecast Projections. Provides automated variance reconciliation classifying discrepancy drivers (`USAGE_DRIFT`, `RATE_CHANGE`, `DISCOUNT_APPLIED`, `NEW_METERS`, `TAXES_CREDITS`).
5. **Cost-Aware Dependency Topology:** Directed acyclic service graph calculating:
   $$\text{Direct Cost} + \text{Dependent Costs} = \text{Total Application Cost}$$
6. **Configurable Multi-Band Thresholds:** Configurable color states (`GREEN` <75%, `AMBER` 75-90%, `ORANGE` 90-100%, `RED` >100%, `GREY` Stale) with hysteresis buffering to prevent alert flapping.
7. **16-Step Guided Onboarding Wizard:** Fully validated step-by-step onboarding pipeline verifying credentials, testing permissions, scanning hierarchies, and scheduling synchronizations.
8. **Enterprise RBAC & Auditing:** 9 built-in enterprise roles (`SUPER_ADMIN`, `PLATFORM_ADMIN`, `CLOUD_ADMIN`, `FINOPS_ADMIN`, `FINANCE_USER`, `IT_OPERATIONS`, `APP_OWNER`, `READ_ONLY`, `AUDITOR`) and an immutable append-only audit trail.

---

## 2. Technology Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2 (Strict DTOs), SQLAlchemy 2.0, Alembic, Tenacity (Exponential Backoff with Jitter).
- **Database:** PostgreSQL 16 (Production) / SQLite (Zero-friction local dev).
- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS (Enterprise ceramic design system), Lucide icons.
- **Security:** JWT authentication, PBKDF2 password hashing, AES-256-GCM credential encryption, OWASP input sanitization, PII masking in structured JSON logs.
- **Containerization:** Docker, Docker Compose.

---

## 3. The Vertical Slice End-to-End User Flow

The complete vertical slice requested in the specification is fully functional and interactive:

$$\text{Login} \longrightarrow \text{Dashboard} \longrightarrow \text{Cloud Provider} \longrightarrow \text{Hierarchy} \longrightarrow \text{Service} \longrightarrow \text{Pricing} \longrightarrow \text{Cost} \longrightarrow \text{Budget} \longrightarrow \text{Threshold} \longrightarrow \text{Detail (360°)}$$

1. **Login:** Corporate JWT authentication with RBAC role authorization.
2. **Dashboard (`/`):** Executive KPIs (Total Cloud Cost, Billed Actuals, Estimated Rates, Run-Rate Forecast, Budget Utilization, Top Cost Drivers).
3. **Cloud Provider (`/providers/[provider]`):** Dedicated cockpits for Azure, AWS, GCP, and OCI with live sync controls.
4. **Hierarchy (`/hierarchy`):** Interactive recursive tree drill-down with node inspector and roll-up scopes.
5. **Service Inventory (`/services`):** Searchable, filterable table with custom search, pricing status badges, threshold badges, and ⓘ icons.
6. **Pricing & Simulation (`/calculator`):** Interactive "What Will This Cost?" simulator with mathematical breakdown.
7. **Cost Cockpit (`/costs`):** FOCUS 1.4 invoice reconciliation engine, variance analysis, and 6-month statistical forecast.
8. **Budgets & Thresholds (`/budgets`):** Hierarchical budgets, progress bars, and interactive hysteresis state machine simulator.
9. **Dependencies (`/dependencies`):** Cost-aware topology graph showing cumulative total application cost.
10. **Service Detail (`/services/[id]`):** 360° Resource view covering Overview, Provider, Pricing, Cost, Usage Telemetry, Runtime Schedules, Dependencies, Alerts, and Audit history.

---

## 4. Getting Started Locally

### Prerequisites
- Python 3.11+
- Node.js 18+ and `pnpm` (or `npm`)
- Git

### Option A: Direct Local Execution (Fastest)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/organization/Cloud-Service-Cost-Management.git
   cd Cloud-Service-Cost-Management
   ```

2. **Initialize Database and Seed Multi-Cloud Demo Estate:**
   ```bash
   python scripts/seed_demo_data.py
   ```
   *This seeds a realistic multi-cloud estate across Azure, AWS, GCP, and OCI with 27 resources, 16 services, FOCUS cost records, telemetry, budgets, alerts, and dependency chains.*

3. **Start FastAPI Backend (Terminal 1):**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - API Gateway: `http://localhost:8000`
   - Interactive Swagger OpenAPI Docs: `http://localhost:8000/docs`

4. **Start Next.js Frontend (Terminal 2):**
   ```bash
   cd frontend
   pnpm dev
   ```
   - Application Web UI: `http://localhost:3000`

5. **Alternatively, use the single-click PowerShell launcher:**
   ```powershell
   .\scripts\run_local.ps1
   ```

---

### Option B: Docker Compose Deployment

Run the complete containerized platform stack (PostgreSQL 16, Redis, Backend, and Frontend):

```bash
docker compose -f infrastructure/docker-compose.yml up --build -d
```

- Web UI: `http://localhost:3000`
- REST API: `http://localhost:8000`
- Database: `localhost:5432` (`cloudscope` / `cloudscope_secure_pass_2026!`)

---

## 5. Automated Test Suite

Run the complete test suite verifying the pricing engine, cost horizons, multi-band thresholds, actual-vs-estimated reconciliation, and all API endpoints:

```bash
# Run backend pytest suite
pytest backend/tests -v

# Run frontend production build validation
cd frontend
pnpm build
```

Or run the all-in-one test script:
```powershell
.\scripts\run_tests.ps1
```

All 22 test scenarios pass with zero errors:
- `test_free_service_status`
- `test_free_tier_and_conditional_free_service`
- `test_paid_service_status_and_calculation`
- `test_tiered_pricing_calculation`
- `test_missing_pricing_status`
- `test_cost_horizons`
- `test_threshold_state_machine_and_hysteresis`
- `test_budget_threshold_and_alerts`
- `test_actual_vs_estimated_reconciliation`
- `test_what_if_simulation`
- `test_health_endpoint`
- `test_auth_login`
- `test_providers_endpoints`
- `test_hierarchy_tree`
- `test_resources_inventory_and_filters`
- `test_resource_explanation_endpoint`
- `test_cost_summary_kpi`
- `test_what_if_simulation_api`
- `test_dependencies_graph`
- `test_alerts_lifecycle`
- `test_onboarding_wizard_step`
- `test_reports_csv_download`

---

## 6. Default Demo Credentials

- **Email:** `admin@cloudscope.internal`
- **Password:** `CloudScope2026!`
- **Role:** `SUPER_ADMIN`
- **Tenant:** Global Enterprise FinOps Corp

---

## 7. Documentation Index

- [`docs/requirements-mapping.md`](docs/requirements-mapping.md) — 100% bidirectional traceability between BBP/FS CS-BBP-FS-001 and software implementation.
- [`docs/architecture.md`](docs/architecture.md) — System architecture, canonical domain ERD, security design, and observability model.
- [`docs/implementation-roadmap.md`](docs/implementation-roadmap.md) — Phased milestones, quality verification gates, and vertical slice definition.

---

## 8. License

Apache License 2.0. Open-source enterprise cloud cost governance platform.
