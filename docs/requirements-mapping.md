# CloudScope: Requirements Traceability & Implementation Mapping Matrix

**Document ID:** CS-REQ-MAP-001  
**Version:** 1.0.0  
**Research & Specification Baseline:** BBP/FS CS-BBP-FS-001, FOCUS 1.4, Provider APIs (Azure, AWS, GCP, OCI)  
**Date:** September 2026  

---

## 1. Executive Summary & Scope

CloudScope is an enterprise multi-cloud service inventory, pricing intelligence, cost governance, runtime/usage monitoring, budgeting, threshold, and dependency mapping platform supporting:
1. **Microsoft Azure**
2. **Amazon Web Services (AWS)**
3. **Google Cloud Platform (GCP)**
4. **Oracle Cloud Infrastructure (OCI)**

This document establishes 100% bidirectional traceability between the Business Blueprint / Functional Specification (BBP/FS) and the software engineering implementation artifacts.

---

## 2. Comprehensive Requirements Traceability Matrix

| Req ID | Domain / Area | BBP/FS Ref | Specification Summary | Implementation Component | Verification / Test Strategy |
|---|---|---|---|---|---|
| **REQ-01** | Multi-Cloud Hierarchy | BBP §225-342, FS §1486-1498 | Preserve native hierarchies (Azure Tenant→MG→Sub→RG; AWS Org→OU→Acct; GCP Org→Folder→Project; OCI Tenancy→Compartment) with Canonical `ResourceNode` layer. | `backend/app/models/hierarchy.py`, `backend/app/services/hierarchy_service.py`, `frontend/src/pages/hierarchy` | Unit test hierarchy builder; verify native path lineage & parent-child cycles. |
| **REQ-02** | Resource Identity & Lineage | FS §343-360, §1437-1458 | Dual identity strategy: immutable provider `native_id` and collision-resistant `canonical_id` (SHA256 of provider+scope+native_id), observed timestamp, deleted timestamp. | `backend/app/models/resource.py`, `backend/app/services/resource_service.py` | Idempotency tests; soft deletion tests; multi-account collision tests. |
| **REQ-03** | Service Catalog & Meter Taxonomy | BBP §361-423, FS §1035-1070 | Standardized Service Family, Service, and Meter classifications mapped to provider SKUs (vCPU-hour, GB-month, request, egress, etc.). | `backend/app/models/service_catalog.py`, `backend/app/models/pricing.py` | Catalog ingestion tests for Azure Retail Prices, AWS Price List, GCP Catalog, OCI List. |
| **REQ-04** | Pricing Intelligence | User Req §3, §4, §5, BBP §1035 | Pricing statuses: `FREE`, `FREE_TIER`, `CONDITIONAL_FREE`, `PAID`, `ESTIMATED`, `UNKNOWN`, `NOT_APPLICABLE`. Detailed explanation breakdown. | `backend/app/services/pricing_engine.py`, `frontend/src/components/PricingInfoModal.tsx` | Unit tests for each status evaluation; verify explanation generator against real SKU data. |
| **REQ-05** | Information Icon (ⓘ) Explanations | User Req §5, §52 | Tooltips, popovers, and side panels explaining "Why does this service cost this amount?" with unit price, billing model, formulas, and dependencies. | `frontend/src/components/CostExplanationModal.tsx`, `frontend/src/components/InfoTooltip.tsx` | UI interaction test; audit math transparency. |
| **REQ-06** | Cost Engine & Formulas | User Req §6, §7, BBP §380-398 | Calculation engine supporting Hourly, Daily, Monthly, Annualized costs across instance, request, volume, and tiered pricing models. | `backend/app/services/cost_engine.py` | Unit tests comparing expected vs calculated sums across all 4 time horizons. |
| **REQ-07** | Cost Categorization | User Req §7, BBP §1459-1485 | Explicit distinct cost states: `Actual` (provider billing), `Estimated` (usage × price), `Forecast` (trend projection), `Manual` (override). | `backend/app/models/cost.py`, `frontend/src/components/CostStateBadge.tsx` | Cost record validation; ensure estimates are never flagged as actuals. |
| **REQ-08** | Cost Reconciliation Engine | User Req §8, BBP §1839-1842 | Reconciles Estimated vs Actual provider costs, recording variance amount, variance %, driver classification (rate, usage, discount, credit). | `backend/app/services/reconciliation_service.py`, `frontend/src/pages/reconciliation` | Variance computation tests; discrepancy tolerance checks. |
| **REQ-09** | FOCUS 1.4 Normalization | User Req §49, BBP §1459-1485 | Ingest and normalize cost records into FinOps FOCUS 1.4 specification while preserving provider-native raw JSON extensions. | `backend/app/schemas/focus.py`, `backend/app/services/focus_normalizer.py` | Schema compliance tests using FOCUS 1.4 test matrices. |
| **REQ-10** | Runtime Monitoring Model | User Req §28, BBP §424-440 | Support 24x7, Scheduled (e.g. M-F 8-18), Seasonal, Event-Driven, and Consumption runtime profiles. Detect schedule deviations. | `backend/app/models/runtime.py`, `backend/app/services/runtime_monitor.py` | Schedule evaluation tests; off-hours drift detection tests. |
| **REQ-11** | Usage & Telemetry Model | User Req §29, BBP §441-462 | Capture CPU, Memory, Storage GB, Requests, IOPS, Network Egress, and provider-specific telemetry metrics over time. | `backend/app/models/usage.py`, `backend/app/services/usage_service.py` | Metric aggregation tests; time-series downsampling tests. |
| **REQ-12** | Budget Engine | User Req §25, BBP §501-532 | Hierarchical budgets definable at Org, Cloud Account, Project/Sub, Service, Application, Cost Center. Inheritance & utilization tracking. | `backend/app/models/budget.py`, `backend/app/services/budget_service.py` | Multi-level hierarchy roll-up tests; child-parent coverage validation. |
| **REQ-13** | Threshold & Color Engine | User Req §26, §27, FS §479-500 | Multi-band thresholds (`Green` <75%, `Amber` 75-90%, `Orange` 90-100%, `Red` >100%, `Grey` Stale/No Data). Supports hysteresis and overrides. | `backend/app/services/threshold_engine.py` | State machine transition tests; hysteresis boundary condition tests. |
| **REQ-14** | Dependency Engine & Graph | User Req §30, §31, §32 | Service topology graph (`DEPENDS_ON`, `CONNECTS_TO`, `SHARED_BY`, `HOSTED_ON`, `BILLS_TO`). Calculate cumulative total application cost. | `backend/app/services/dependency_engine.py`, `frontend/src/pages/dependencies` | Directed acyclic graph traversal; cumulative cost aggregation tests. |
| **REQ-15** | Alert Engine & Lifecycle | User Req §33, FS §937-970 | Alert rules (Budget breach, Forecast breach, Cost spike, Runtime drift, Stale data). States: `CREATED`→`OPEN`→`ACKNOWLEDGED`→`RESOLVED`. | `backend/app/models/alert.py`, `backend/app/services/alert_service.py` | Alert generation on threshold breach; lifecycle transition audit tests. |
| **REQ-16** | 16-Step Onboarding Wizard | User Req §16, BBP §551-640 | Guided 16-step onboarding wizard for Azure, AWS, GCP, OCI with credential test, permission validation, hierarchy scan, and sync setup. | `frontend/src/pages/onboarding`, `backend/app/api/v1/onboarding.py` | End-to-end wizard mock execution; validation error handling tests. |
| **REQ-17** | Cloud Connector Architecture | User Req §13, §15, FS §1486 | Standard `CloudConnector` abstraction. Concrete connectors for Azure, AWS, GCP, OCI with connection pooling, retries, and rate limiting. | `backend/app/connectors/base.py`, `backend/app/connectors/{azure,aws,gcp,oci}.py` | Mock and live API interface conformance tests; timeout and retry tests. |
| **REQ-18** | Demo / Mock Provider Mode | User Req §14, §45 | Fully realistic mock cloud environments for all 4 providers with realistic hierarchies, services, SKUs, telemetry, budgets, alerts, and graphs. | `backend/app/connectors/demo_adapter.py`, `scripts/seed_demo_data.py` | Instant database seeding; verification of all 4 cloud provider estates. |
| **REQ-19** | Background Sync & Freshness | User Req §17, §18, §19 | Scheduled and on-demand synchronization jobs. Tracking freshness timestamps (`Current`, `Stale`, `Failed`) with freshness SLA labels. | `backend/app/services/sync_orchestrator.py`, `backend/app/models/sync_job.py` | Sync job execution tests; staleness warning trigger tests. |
| **REQ-20** | Service Inventory & Explorer | User Req §20, §41 | Paginated, filterable, sortable service and resource inventory table with multi-cloud search, custom columns, and CSV export. | `frontend/src/pages/services`, `backend/app/api/v1/services.py` | Search query benchmarks; pagination and filter combination tests. |
| **REQ-21** | Service Detail 360° View | User Req §21 | Complete service page: Overview, Provider, Pricing, Cost, Usage, Runtime, Dependency, Connectivity, Alerts, Audit history. | `frontend/src/pages/services/[id].tsx` | Route integration test; component rendering test with complete data. |
| **REQ-22** | Executive & Cloud Dashboards | User Req §22, §23, §24 | Executive KPI dashboard, provider-specific dashboards, cost cockpit with daily/monthly spend charts, top drivers, and drill-down links. | `frontend/src/pages/dashboard`, `frontend/src/pages/providers/[provider].tsx` | Chart data aggregation tests; interactive drill-down navigation tests. |
| **REQ-23** | Cost Forecasting Engine | User Req §40, BBP §987-1002 | Explainable run-rate and moving average forecasting with confidence bands, methodology metadata, and budget breach warnings. | `backend/app/services/forecast_engine.py` | Statistical forecasting accuracy tests; confidence interval checks. |
| **REQ-24** | What-If Cost Calculator | User Req §53, §54 | Interactive cost simulation: select service, region, instance/tier, runtime hours, storage volume, and calculate hourly/monthly/annual totals. | `backend/app/services/whatif_simulator.py`, `frontend/src/pages/calculator` | What-if simulation mathematical verification against catalog rates. |
| **REQ-25** | Admin Console, RBAC & Audit | User Req §34, §35, §36 | 9 enterprise roles (Super Admin, FinOps Admin, etc.), permission scoping, administrative overrides with audit logs, and system settings. | `backend/app/models/audit.py`, `backend/app/core/rbac.py`, `frontend/src/pages/admin` | Unauthorized access rejection tests (HTTP 403); audit trail completeness tests. |
| **REQ-26** | Security & Secret Handling | User Req §37, Enterprise Rules | JWT auth, PBKDF2/bcrypt hashing, AES-GCM credential encryption, structured JSON logging with PII masking, OWASP sanitization. | `backend/app/core/security.py`, `backend/app/core/logging_config.py` | Encryption/decryption tests; logging sanitization tests; SQL injection safety. |
| **REQ-27** | Reporting & Export Engine | User Req §42, FS §971-986 | Comprehensive reporting engine generating CSV and JSON exports for Costs, Budgets, Forecasts, Services, and Governance alerts. | `backend/app/services/report_service.py`, `frontend/src/pages/reports` | Export formatting tests; streamed CSV download tests. |
| **REQ-28** | Local Dev & Containerization | User Req §11, §44 | Docker Compose configuration with PostgreSQL, Redis, Backend, Frontend, and worker; native zero-friction execution script. | `docker-compose.yml`, `scripts/run_local.ps1`, `Dockerfile` | Container build and startup validation; healthcheck verification. |

---

## 3. Provider-Specific Technical Specifications

### 3.1 Microsoft Azure
- **Hierarchy:** Tenant (Azure Entra ID) → Root Management Group → Management Groups → Subscriptions → Resource Groups → Resources.
- **Inventory API:** Azure Resource Graph (`Resources` table query) & ARM Resource Management API `2024-03-01`.
- **Pricing API:** Azure Retail Prices REST API (`https://prices.azure.com/api/retail/prices`), no auth required for public catalog lookup; ARM Price Sheets for EA/MCA contract rates.
- **Cost & Usage API:** Azure Cost Management Exports API / Cost Details API (`2023-11-01`) producing FOCUS-compatible or CSV blob exports.
- **Budgets API:** Azure Consumption / Cost Management Budgets API (`2023-11-01`).
- **Telemetry / Metrics:** Azure Monitor REST API (`2018-01-01`) for `Percentage CPU`, `Network In/Out`, `Disk Read/Write Bytes`.

### 3.2 Amazon Web Services (AWS)
- **Hierarchy:** AWS Organizations (Root) → Organizational Units (OUs) → Accounts → Regions → VPCs/Resource Groups → Resources.
- **Inventory API:** AWS Resource Explorer (`resource-explorer-2:Search`), AWS Config (`config:SelectResourceConfig`), and direct service SDKs (EC2, RDS, S3, Lambda).
- **Pricing API:** AWS Price List Service API (`pricing:GetProducts`, `pricing:GetAttributeValues`) in `us-east-1` and `eu-central-1`.
- **Cost & Usage API:** AWS Data Exports (CUR 2.0 / FOCUS 1.4 exports to S3) & AWS Cost Explorer API (`ce:GetCostAndUsage`).
- **Budgets API:** AWS Budgets API (`budgets:ViewBudget`, `budgets:DescribeBudgets`).
- **Telemetry / Metrics:** Amazon CloudWatch Metrics (`cloudwatch:GetMetricData`).

### 3.3 Google Cloud Platform (GCP)
- **Hierarchy:** Cloud Identity / Workspace Organization → Folders (nested) → Projects → Regions/Zones → Resources.
- **Inventory API:** Cloud Asset Inventory API (`cloudasset.googleapis.com/v1/assets:searchAllResources`).
- **Pricing API:** Cloud Billing Catalog API (`cloudbilling.googleapis.com/v1/services/{service_id}/skus`).
- **Cost & Usage API:** Cloud Billing Export to BigQuery (Standard and Detailed usage cost) normalized to FOCUS.
- **Budgets API:** Cloud Billing Budget API (`billingbudgets.googleapis.com/v1/billingAccounts/{account_id}/budgets`).
- **Telemetry / Metrics:** Google Cloud Monitoring API (`monitoring.googleapis.com/v3/projects/{project_id}/timeSeries`).

### 3.4 Oracle Cloud Infrastructure (OCI)
- **Hierarchy:** Tenancy (Root Compartment) → Compartments (nested up to 6 levels) → Regions / Availability Domains → Resources.
- **Inventory API:** OCI Search / Resource Discovery Service (`SearchResources` / `ListResources`).
- **Pricing API:** OCI Public Rate Card / Meter API and Cost Analysis List Pricing API.
- **Cost & Usage API:** OCI Usage API (`usageapi:RequestSummarizedUsages`) and Cost & Usage Reports (FOCUS 1.4 CSV in Object Storage).
- **Budgets API:** OCI Budgets API (`ListBudgets`, `GetBudget`).
- **Telemetry / Metrics:** OCI Monitoring Service (`SummarizeMetricsData`).

---

## 4. Ambiguities, Contradictions & Provider Limitations Resolved

1. **Hierarchy Abstraction vs Native Parity:**
   - *Problem:* Azure has Resource Groups; AWS does not natively require them; GCP has Folders and Projects; OCI has Compartments.
   - *Resolution:* CloudScope models every hierarchical level as a `ResourceNode` with a native `node_type` (`management_group`, `subscription`, `resource_group`, `organization`, `ou`, `account`, `folder`, `project`, `tenancy`, `compartment`) and a canonical role (`GOVERNANCE_ROOT`, `GOVERNANCE_GROUP`, `BILLING_CONTEXT`, `RESOURCE_CONTAINER`, `RESOURCE`).
2. **Billing Latency vs Operational Monitoring:**
   - *Problem:* Cloud billing data (CUR, Azure Cost Exports, GCP BQ Export) is typically delayed by 6 to 24 hours, whereas operational usage/metrics are near real-time (5 to 15 min).
   - *Resolution:* Clear separation of `CostRecord` (authoritative actuals from billing pipelines) vs `UsageMetric` (telemetry observations) vs `EstimatedCost` (calculated real-time as `metric_volume × catalog_price`). Freshness badges explicitly inform the user of the timestamp and source of every data point.
3. **Commitments, Savings Plans & Blended Rates:**
   - *Problem:* Naive unit price multiplication ignores customer-specific Enterprise Agreements, Savings Plans, and Reserved Instances.
   - *Resolution:* CloudScope follows the FinOps FOCUS 1.4 standard: explicitly showing `ListUnitPrice`, `ContractedUnitPrice`, `BilledCost`, and `EffectiveCost`. When unbilled, the system displays `ESTIMATED (List Rate)` with an information icon (ⓘ) detailing assumptions.
