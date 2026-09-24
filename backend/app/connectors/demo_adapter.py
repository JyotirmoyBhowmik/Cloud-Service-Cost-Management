"""
Multi-Cloud Demo Generator & Seed Adapter
Generates complete realistic cloud estates for Azure, AWS, GCP, and OCI per User Request §14, §45.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.tenant_user import Tenant, User
from app.models.connector import Connector
from app.models.hierarchy import ResourceNode
from app.models.service_pricing import Service, PricingSKU, PricingTier
from app.models.cost import CostRecord, ReconciliationRecord, ForecastRecord
from app.models.usage_runtime import UsageMetric, RuntimeRecord
from app.models.budget_threshold import Budget, ThresholdRule
from app.models.dependency import DependencyEdge
from app.models.alert import Alert, Policy
from app.core.security import hash_password


class DemoDataGenerator:
    """
    Seeds database with enterprise multi-cloud estates across Azure, AWS, GCP, and OCI.
    """

    @staticmethod
    def seed_complete_demo_estate(db: Session) -> Tenant:
        """Populates all 4 clouds with native hierarchies, services, SKUs, costs, telemetry, and graphs."""
        # 1. Tenant & Users
        tenant = db.query(Tenant).filter(Tenant.slug == "enterprise-global").first()
        if not tenant:
            tenant = Tenant(
                name="Global Enterprise FinOps Corp",
                slug="enterprise-global",
                default_currency="USD",
                settings={"data_retention_days": 365, "freshness_sla_hours": 24}
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        # Admin user
        admin = db.query(User).filter(User.email == "admin@cloudscope.internal").first()
        if not admin:
            admin = User(
                tenant_id=tenant.id,
                email="admin@cloudscope.internal",
                full_name="Enterprise FinOps Architect",
                hashed_password=hash_password("CloudScope2026!"),
                role="SUPER_ADMIN",
                is_active=True,
            )
            db.add(admin)
            db.commit()

        # 2. Provider Connectors (All 4 in Healthy/Connected status)
        providers_meta = [
            ("AZURE", "Azure Commercial Production", "SERVICE_PRINCIPAL", {"tenant_id": "72f988bf-86f1-41af-91ab-2d7cd011db47", "subscription_id": "sub-az-prod-001"}),
            ("AWS", "AWS Primary Production Org", "IAM_ROLE", {"account_id": "491029384712", "region": "us-east-1"}),
            ("GCP", "Google Cloud Enterprise Workloads", "SERVICE_ACCOUNT", {"project_id": "gcp-corp-prod-789", "org_id": "384910294"}),
            ("OCI", "Oracle Cloud Tenancy Commercial", "API_KEY", {"tenancy_ocid": "ocid1.tenancy.oc1..aaaaaaaamodemo", "user_ocid": "ocid1.user.oc1..demo"}),
        ]
        
        connector_map: Dict[str, Connector] = {}
        for prov_code, name, auth, cfg in providers_meta:
            conn = db.query(Connector).filter(Connector.tenant_id == tenant.id, Connector.provider == prov_code).first()
            if not conn:
                conn = Connector(
                    tenant_id=tenant.id,
                    provider=prov_code,
                    name=name,
                    auth_method=auth,
                    status="HEALTHY",
                    config=cfg,
                    last_successful_sync=datetime.now(timezone.utc) - timedelta(minutes=15),
                    last_attempted_sync=datetime.now(timezone.utc) - timedelta(minutes=15),
                    resource_count=12,
                    service_count=4,
                    pricing_status="HEALTHY",
                    cost_status="HEALTHY",
                    usage_status="HEALTHY",
                )
                db.add(conn)
                db.commit()
                db.refresh(conn)
            connector_map[prov_code] = conn

        # 3. Service Catalogs & SKUs (Azure, AWS, GCP, OCI)
        services_def = [
            # Azure
            ("AZURE", "Virtual Machines", "Azure Virtual Machines", "Compute", "PER_HOUR", False, "", "Standard_D4s_v5", "Standard D4s v5 (4 vCPU, 16GB)", 0.1920, "1 Hour", "eastus"),
            ("AZURE", "SQL Database", "Azure SQL Managed Instance", "Database", "PER_HOUR", False, "", "GP_Gen5_4", "General Purpose Gen5 4 vCore", 0.4950, "1 Hour", "eastus"),
            ("AZURE", "Storage Accounts", "Azure Blob Storage Standard", "Storage", "PER_GB_MONTH", True, "First 5 GB free per month", "Hot-LRS", "Hot LRS Storage", 0.0180, "1 GB-Month", "eastus"),
            ("AZURE", "Application Gateway", "Azure App Gateway Standard v2", "Network", "PER_HOUR", False, "", "Standard_v2", "Application Gateway Standard v2", 0.2460, "1 Hour", "eastus"),
            # AWS
            ("AWS", "AmazonEC2", "Amazon Elastic Compute Cloud (EC2)", "Compute", "PER_HOUR", True, "750 hours t2.micro / t3.micro free for 12 mos", "t3.xlarge", "t3.xlarge General Purpose", 0.1664, "1 Hour", "us-east-1"),
            ("AWS", "AmazonRDS", "Amazon Relational Database Service (RDS)", "Database", "PER_HOUR", False, "", "db.r5.large", "db.r5.large Multi-AZ PostgreSQL", 0.5800, "1 Hour", "us-east-1"),
            ("AWS", "AmazonS3", "Amazon Simple Storage Service (S3)", "Storage", "PER_GB_MONTH", True, "5 GB Standard Storage free", "Standard-ByteHrs", "S3 Standard Storage", 0.0230, "1 GB-Month", "us-east-1"),
            ("AWS", "AWSELB", "Elastic Load Balancing (ALB)", "Network", "PER_HOUR", False, "", "LoadBalancerUsage", "Application Load Balancer", 0.0225, "1 Hour", "us-east-1"),
            # GCP
            ("GCP", "Compute Engine", "Google Compute Engine (GCE)", "Compute", "PER_HOUR", True, "e2-micro instance free each month", "n2-standard-4", "N2 Standard 4 (4 vCPU, 16GB)", 0.1948, "1 Hour", "us-central1"),
            ("GCP", "Cloud SQL", "Google Cloud SQL for PostgreSQL", "Database", "PER_HOUR", False, "", "db-custom-4-16384", "Custom 4 vCPU 16GB Dedicated", 0.4320, "1 Hour", "us-central1"),
            ("GCP", "Cloud Storage", "Google Cloud Storage Standard", "Storage", "PER_GB_MONTH", True, "5 GB free Standard Storage per month", "Standard-Storage", "Standard Regional Storage", 0.0200, "1 GB-Month", "us-central1"),
            ("GCP", "Cloud Load Balancing", "Google Cloud Load Balancing", "Network", "PER_HOUR", False, "", "ForwardingRules", "Global Forwarding Rule", 0.0250, "1 Hour", "us-central1"),
            # OCI
            ("OCI", "Compute", "OCI Flexible Virtual Machine", "Compute", "PER_HOUR", True, "3,000 OCPU hours Always Free on Ampere A1", "VM.Standard.E4.Flex", "VM.Standard.E4.Flex (4 OCPU, 64GB)", 0.1200, "1 Hour", "us-ashburn-1"),
            ("OCI", "Autonomous Database", "OCI Autonomous Transaction Processing", "Database", "PER_HOUR", True, "2 Always Free Autonomous Databases", "ATP.Shared", "Autonomous DB Serverless 1 ECPU", 0.3360, "1 Hour", "us-ashburn-1"),
            ("OCI", "Object Storage", "OCI Object Storage Standard", "Storage", "PER_GB_MONTH", True, "10 GB Always Free Storage", "Standard-Object", "Standard Tier Object Storage", 0.0255, "1 GB-Month", "us-ashburn-1"),
            ("OCI", "Virtual Cloud Network", "OCI Flexible Load Balancer", "Network", "PER_HOUR", True, "1 Always Free 10Mbps Load Balancer", "LB-100Mbps", "Flexible Load Balancer 100Mbps", 0.0113, "1 Hour", "us-ashburn-1"),
        ]

        sku_db_map: Dict[str, PricingSKU] = {}
        service_db_map: Dict[str, Service] = {}

        for prov, scode, sname, fam, pmod, has_ft, ft_desc, skuid, skunm, uprice, bunit, rgn in services_def:
            key = f"{prov}:{scode}"
            srv = db.query(Service).filter(Service.provider == prov, Service.service_code == scode).first()
            if not srv:
                srv = Service(
                    provider=prov,
                    service_code=scode,
                    service_name=sname,
                    service_family=fam,
                    default_pricing_model=pmod,
                    has_free_tier=has_ft,
                    free_tier_description=ft_desc,
                )
                db.add(srv)
                db.commit()
                db.refresh(srv)
            service_db_map[key] = srv

            # SKU
            sku = db.query(PricingSKU).filter(PricingSKU.provider == prov, PricingSKU.provider_sku_id == skuid).first()
            if not sku:
                sku = PricingSKU(
                    service_id=srv.id,
                    provider=prov,
                    provider_sku_id=skuid,
                    sku_name=skunm,
                    meter_name=skunm,
                    pricing_model=pmod,
                    billing_unit=bunit,
                    unit_price=uprice,
                    currency="USD",
                    region=rgn,
                    is_free=False,
                    free_allowance_units=5.0 if has_ft else 0.0,
                    free_allowance_description=ft_desc,
                    pricing_source=f"{prov}_RETAIL_CATALOG",
                )
                db.add(sku)
                db.commit()
                db.refresh(sku)
            sku_db_map[key] = sku

        # 4. Realistic Hierarchies & Resources per User Request §45
        # AZURE: Mgmt Group -> Subscription -> Resource Group -> VM, DB, Storage, LB
        az_conn = connector_map["AZURE"]
        az_nodes = [
            ("az-mg-root", "/providers/Microsoft.Management/managementGroups/mg-enterprise-root", "Enterprise Root MG", "management_group", "GOVERNANCE_ROOT", None, "eastus", "production", "FinOps Corp", "CC-AZ-001"),
            ("az-sub-prod", "/subscriptions/092834-prod-core-sub", "Production-Subscription-01", "subscription", "BILLING_CONTEXT", "az-mg-root", "eastus", "production", "FinOps Corp", "CC-AZ-001"),
            ("az-rg-ecommerce", "/subscriptions/092834/resourceGroups/rg-ecommerce-prod", "rg-ecommerce-prod", "resource_group", "RESOURCE_CONTAINER", "az-sub-prod", "eastus", "production", "E-Commerce", "CC-AZ-101"),
            ("az-vm-web", "/subscriptions/092834/resourceGroups/rg-ecommerce-prod/providers/Microsoft.Compute/virtualMachines/vm-az-web-01", "vm-az-web-01", "virtual_machine", "RESOURCE", "az-rg-ecommerce", "eastus", "production", "E-Commerce", "CC-AZ-101"),
            ("az-sql-prod", "/subscriptions/092834/resourceGroups/rg-ecommerce-prod/providers/Microsoft.Sql/servers/sql-az-prod/databases/db-orders", "sql-az-orders-db", "sql_database", "RESOURCE", "az-rg-ecommerce", "eastus", "production", "E-Commerce", "CC-AZ-101"),
            ("az-blob-data", "/subscriptions/092834/resourceGroups/rg-ecommerce-prod/providers/Microsoft.Storage/storageAccounts/stazordersmedia", "stazordersmedia", "storage_account", "RESOURCE", "az-rg-ecommerce", "eastus", "production", "E-Commerce", "CC-AZ-101"),
            ("az-appgw-front", "/subscriptions/092834/resourceGroups/rg-ecommerce-prod/providers/Microsoft.Network/applicationGateways/appgw-az-front", "appgw-az-front", "application_gateway", "RESOURCE", "az-rg-ecommerce", "eastus", "production", "E-Commerce", "CC-AZ-101"),
        ]

        # AWS: Org -> Production OU -> Account -> VPC -> EC2, RDS, S3, ALB
        aws_conn = connector_map["AWS"]
        aws_nodes = [
            ("aws-org-root", "arn:aws:organizations::491029384712:root/o-89472910/r-root", "Global Corp Org Root", "organization", "GOVERNANCE_ROOT", None, "us-east-1", "production", "FinOps Corp", "CC-AWS-001"),
            ("aws-ou-prod", "arn:aws:organizations::491029384712:ou/o-89472910/ou-prod-992", "Production-Workloads-OU", "ou", "GOVERNANCE_GROUP", "aws-org-root", "us-east-1", "production", "FinOps Corp", "CC-AWS-001"),
            ("aws-acct-banking", "arn:aws:organizations::491029384712:account/o-89472910/112233445566", "AWS-Core-Banking (112233445566)", "account", "BILLING_CONTEXT", "aws-ou-prod", "us-east-1", "production", "Banking Systems", "CC-AWS-502"),
            ("aws-ec2-api", "arn:aws:ec2:us-east-1:112233445566:instance/i-0a892b19283c7491", "ec2-banking-api-prod-01", "ec2_instance", "RESOURCE", "aws-acct-banking", "us-east-1", "production", "Banking Systems", "CC-AWS-502"),
            ("aws-rds-pg", "arn:aws:rds:us-east-1:112233445566:db:rds-banking-ledger-db", "rds-banking-ledger-db", "rds_instance", "RESOURCE", "aws-acct-banking", "us-east-1", "production", "Banking Systems", "CC-AWS-502"),
            ("aws-s3-docs", "arn:aws:s3:::aws-banking-audit-archives-2026", "aws-banking-audit-archives", "s3_bucket", "RESOURCE", "aws-acct-banking", "us-east-1", "production", "Banking Systems", "CC-AWS-502"),
            ("aws-alb-gw", "arn:aws:elasticloadbalancing:us-east-1:112233445566:loadbalancer/app/alb-banking-public/9a8b7c", "alb-banking-public", "load_balancer", "RESOURCE", "aws-acct-banking", "us-east-1", "production", "Banking Systems", "CC-AWS-502"),
        ]

        # GCP: Org -> Folder -> Project -> Compute, Cloud SQL, Cloud Storage, LB
        gcp_conn = connector_map["GCP"]
        gcp_nodes = [
            ("gcp-org-root", "//cloudresourcemanager.googleapis.com/organizations/384910294", "Enterprise GCP Org", "organization", "GOVERNANCE_ROOT", None, "us-central1", "production", "FinOps Corp", "CC-GCP-001"),
            ("gcp-folder-prod", "//cloudresourcemanager.googleapis.com/folders/491029481", "Production-Services-Folder", "folder", "GOVERNANCE_GROUP", "gcp-org-root", "us-central1", "production", "FinOps Corp", "CC-GCP-001"),
            ("gcp-proj-analytics", "//cloudresourcemanager.googleapis.com/projects/gcp-corp-prod-789", "gcp-data-analytics-prod", "project", "BILLING_CONTEXT", "gcp-folder-prod", "us-central1", "production", "Data Analytics", "CC-GCP-703"),
            ("gcp-gce-spark", "//compute.googleapis.com/projects/gcp-corp-prod-789/zones/us-central1-a/instances/gce-spark-worker-01", "gce-spark-worker-01", "compute_instance", "RESOURCE", "gcp-proj-analytics", "us-central1", "production", "Data Analytics", "CC-GCP-703"),
            ("gcp-sql-pg", "//cloudsql.googleapis.com/projects/gcp-corp-prod-789/instances/cloudsql-analytics-dw", "cloudsql-analytics-dw", "cloud_sql", "RESOURCE", "gcp-proj-analytics", "us-central1", "production", "Data Analytics", "CC-GCP-703"),
            ("gcp-gcs-lake", "//storage.googleapis.com/b/gcp-corp-data-lake-raw", "gcp-corp-data-lake-raw", "storage_bucket", "RESOURCE", "gcp-proj-analytics", "us-central1", "production", "Data Analytics", "CC-GCP-703"),
            ("gcp-lb-front", "//compute.googleapis.com/projects/gcp-corp-prod-789/global/forwardingRules/gcp-analytics-lb", "gcp-analytics-lb", "load_balancer", "RESOURCE", "gcp-proj-analytics", "us-central1", "production", "Data Analytics", "CC-GCP-703"),
        ]

        # OCI: Tenancy -> Compartment -> Compute, Database, Object Storage, VCN
        oci_conn = connector_map["OCI"]
        oci_nodes = [
            ("oci-ten-root", "ocid1.tenancy.oc1..global-enterprise", "Global-Enterprise-Tenancy", "tenancy", "GOVERNANCE_ROOT", None, "us-ashburn-1", "production", "FinOps Corp", "CC-OCI-001"),
            ("oci-comp-prod", "ocid1.compartment.oc1..prod-workloads", "Prod-Workloads-Compartment", "compartment", "GOVERNANCE_GROUP", "oci-ten-root", "us-ashburn-1", "production", "FinOps Corp", "CC-OCI-001"),
            ("oci-vm-app", "ocid1.instance.oc1.iad.vm-billing-01", "oci-billing-core-01", "compute_instance", "RESOURCE", "oci-comp-prod", "us-ashburn-1", "production", "Enterprise Billing", "CC-OCI-901"),
            ("oci-atp-db", "ocid1.autonomousdatabase.oc1.iad.db-finops", "oci-atp-finops-db", "autonomous_database", "RESOURCE", "oci-comp-prod", "us-ashburn-1", "production", "Enterprise Billing", "CC-OCI-901"),
            ("oci-obj-store", "ocid1.bucket.oc1.iad.billing-invoices-2026", "oci-billing-invoices", "object_storage", "RESOURCE", "oci-comp-prod", "us-ashburn-1", "production", "Enterprise Billing", "CC-OCI-901"),
            ("oci-vcn-lb", "ocid1.loadbalancer.oc1.iad.lb-billing-public", "oci-lb-billing-public", "load_balancer", "RESOURCE", "oci-comp-prod", "us-ashburn-1", "production", "Enterprise Billing", "CC-OCI-901"),
        ]

        # Map to track created ResourceNode entities by canonical ID
        created_nodes: Dict[str, ResourceNode] = {}

        all_node_specs = [
            ("AZURE", az_conn.id, az_nodes),
            ("AWS", aws_conn.id, aws_nodes),
            ("GCP", gcp_conn.id, gcp_nodes),
            ("OCI", oci_conn.id, oci_nodes),
        ]

        # Service mapping lookup for resources
        res_to_service = {
            "az-vm-web": "AZURE:Virtual Machines",
            "az-sql-prod": "AZURE:SQL Database",
            "az-blob-data": "AZURE:Storage Accounts",
            "az-appgw-front": "AZURE:Application Gateway",
            "aws-ec2-api": "AWS:AmazonEC2",
            "aws-rds-pg": "AWS:AmazonRDS",
            "aws-s3-docs": "AWS:AmazonS3",
            "aws-alb-gw": "AWS:AWSELB",
            "gcp-gce-spark": "GCP:Compute Engine",
            "gcp-sql-pg": "GCP:Cloud SQL",
            "gcp-gcs-lake": "GCP:Cloud Storage",
            "gcp-lb-front": "GCP:Cloud Load Balancing",
            "oci-vm-app": "OCI:Compute",
            "oci-atp-db": "OCI:Autonomous Database",
            "oci-obj-store": "OCI:Object Storage",
            "oci-vcn-lb": "OCI:Virtual Cloud Network",
        }

        # Pricing status mapping
        res_pricing_status = {
            "az-blob-data": "FREE_TIER",
            "aws-s3-docs": "FREE_TIER",
            "gcp-gcs-lake": "FREE_TIER",
            "oci-obj-store": "FREE_TIER",
            "oci-vcn-lb": "FREE",
        }

        for prov, conn_id, nodes in all_node_specs:
            for cid, nid, name, ntype, role, pid, rgn, env, bu, cc in nodes:
                node = db.query(ResourceNode).filter(ResourceNode.canonical_id == cid).first()
                parent_db_id = created_nodes[pid].id if pid and pid in created_nodes else None
                srv_key = res_to_service.get(cid)
                srv = service_db_map.get(srv_key) if srv_key else None
                status = res_pricing_status.get(cid, "PAID" if role == "RESOURCE" else "NOT_APPLICABLE")

                if not node:
                    node = ResourceNode(
                        canonical_id=cid,
                        native_id=nid,
                        connector_id=conn_id,
                        provider=prov,
                        name=name,
                        native_type=ntype,
                        canonical_role=role,
                        parent_id=parent_db_id,
                        region=rgn,
                        environment=env,
                        owner="platform-ops@company.com",
                        business_unit=bu,
                        cost_center=cc,
                        service_id=srv.id if srv else None,
                        pricing_status=status,
                        threshold_state="GREEN",
                        last_sync_at=datetime.now(timezone.utc) - timedelta(minutes=15),
                        data_source="API",
                        tags={"Environment": env, "CostCenter": cc, "BusinessUnit": bu},
                    )
                    db.add(node)
                    db.commit()
                    db.refresh(node)
                created_nodes[cid] = node

        # 5. Realistic Cost Records (FOCUS 1.4 Billed Actuals)
        # Give each resource realistic spend
        resource_costs = [
            ("az-vm-web", "AZURE:Virtual Machines", 138.24, 720.0, "Hours"),
            ("az-sql-prod", "AZURE:SQL Database", 356.40, 720.0, "Hours"),
            ("az-blob-data", "AZURE:Storage Accounts", 24.80, 1378.0, "GB-Month"),
            ("az-appgw-front", "AZURE:Application Gateway", 177.12, 720.0, "Hours"),
            ("aws-ec2-api", "AWS:AmazonEC2", 119.81, 720.0, "Hours"),
            ("aws-rds-pg", "AWS:AmazonRDS", 417.60, 720.0, "Hours"),
            ("aws-s3-docs", "AWS:AmazonS3", 48.30, 2100.0, "GB-Month"),
            ("aws-alb-gw", "AWS:AWSELB", 16.20, 720.0, "Hours"),
            ("gcp-gce-spark", "GCP:Compute Engine", 140.26, 720.0, "Hours"),
            ("gcp-sql-pg", "GCP:Cloud SQL", 311.04, 720.0, "Hours"),
            ("gcp-gcs-lake", "GCP:Cloud Storage", 68.40, 3420.0, "GB-Month"),
            ("gcp-lb-front", "GCP:Cloud Load Balancing", 18.00, 720.0, "Hours"),
            ("oci-vm-app", "OCI:Compute", 86.40, 720.0, "Hours"),
            ("oci-atp-db", "OCI:Autonomous Database", 241.92, 720.0, "Hours"),
            ("oci-obj-store", "OCI:Object Storage", 19.50, 800.0, "GB-Month"),
            ("oci-vcn-lb", "OCI:Virtual Cloud Network", 0.00, 720.0, "Hours"),
        ]

        now = datetime.now(timezone.utc)
        p_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        p_end = now

        for cid, srv_key, billed, qty, uunit in resource_costs:
            res_node = created_nodes.get(cid)
            sku = sku_db_map.get(srv_key)
            if res_node:
                # Add Actual Billed Record
                actual_rec = db.query(CostRecord).filter(CostRecord.resource_id == res_node.id, CostRecord.cost_state == "ACTUAL").first()
                if not actual_rec:
                    actual_rec = CostRecord(
                        resource_id=res_node.id,
                        sku_id=sku.id if sku else None,
                        provider=res_node.provider,
                        billing_account_id=f"BA-{res_node.provider}-001",
                        cost_state="ACTUAL",
                        charge_category="Usage",
                        billed_cost=billed,
                        effective_cost=billed,
                        list_cost=billed * 1.02,
                        currency="USD",
                        usage_quantity=qty,
                        usage_unit=uunit,
                        period_start=p_start,
                        period_end=p_end,
                        pricing_status=res_node.pricing_status,
                        calculation_method="PROVIDER_INVOICE",
                    )
                    db.add(actual_rec)

                # Add Estimated Cost Record for reconciliation
                est_cost = round(billed * 0.96, 2)
                est_rec = db.query(CostRecord).filter(CostRecord.resource_id == res_node.id, CostRecord.cost_state == "ESTIMATED").first()
                if not est_rec:
                    est_rec = CostRecord(
                        resource_id=res_node.id,
                        sku_id=sku.id if sku else None,
                        provider=res_node.provider,
                        billing_account_id=f"BA-{res_node.provider}-001",
                        cost_state="ESTIMATED",
                        charge_category="Usage",
                        billed_cost=est_cost,
                        effective_cost=est_cost,
                        list_cost=est_cost,
                        currency="USD",
                        usage_quantity=qty,
                        usage_unit=uunit,
                        period_start=p_start,
                        period_end=p_end,
                        pricing_status=res_node.pricing_status,
                        calculation_method="FORMULA_USAGE_X_RATE",
                    )
                    db.add(est_rec)

                # Add Reconciliation Record
                diff = round(billed - est_cost, 2)
                var_pct = round((diff / est_cost) * 100.0, 2) if est_cost > 0 else 0.0
                rec_record = db.query(ReconciliationRecord).filter(ReconciliationRecord.resource_id == res_node.id).first()
                if not rec_record:
                    rec_record = ReconciliationRecord(
                        resource_id=res_node.id,
                        period="2026-09",
                        provider=res_node.provider,
                        estimated_amount=est_cost,
                        actual_amount=billed,
                        difference=diff,
                        variance_pct=var_pct,
                        driver_type="NEW_METERS" if diff > 10 else "DISCOUNT_APPLIED" if diff < 0 else "EXACT_MATCH",
                        status="RECONCILED" if abs(diff) < 15.0 else "PENDING_REVIEW",
                        notes=f"Reconciled for 2026-09 billing period against {res_node.provider} exports.",
                    )
                    db.add(rec_record)

                # Add Telemetry & Runtime records
                um = db.query(UsageMetric).filter(UsageMetric.resource_id == res_node.id).first()
                if not um:
                    um = UsageMetric(
                        resource_id=res_node.id,
                        metric_name="CPU_UTILIZATION",
                        metric_value=54.5,
                        metric_unit="%",
                        recorded_at=now - timedelta(minutes=10),
                        source=f"{res_node.provider}_MONITORING",
                    )
                    db.add(um)

                rt = db.query(RuntimeRecord).filter(RuntimeRecord.resource_id == res_node.id).first()
                if not rt:
                    rt = RuntimeRecord(
                        resource_id=res_node.id,
                        runtime_profile="24x7",
                        is_running=True,
                        active_hours_today=24.0,
                        active_hours_monthly=720.0,
                        expected_hours_monthly=720.0,
                        schedule_adherence_pct=100.0,
                    )
                    db.add(rt)

        db.commit()

        # 6. Realistic Dependencies (User Request §32 & §45)
        # Application -> Load Balancer -> Compute -> Database -> Storage
        dep_chains = [
            # Azure
            ("az-appgw-front", "az-vm-web", "CONNECTS_TO"),
            ("az-vm-web", "az-sql-prod", "DEPENDS_ON"),
            ("az-vm-web", "az-blob-data", "CONSUMES"),
            # AWS
            ("aws-alb-gw", "aws-ec2-api", "CONNECTS_TO"),
            ("aws-ec2-api", "aws-rds-pg", "DEPENDS_ON"),
            ("aws-ec2-api", "aws-s3-docs", "CONSUMES"),
            # GCP
            ("gcp-lb-front", "gcp-gce-spark", "CONNECTS_TO"),
            ("gcp-gce-spark", "gcp-sql-pg", "DEPENDS_ON"),
            ("gcp-gce-spark", "gcp-gcs-lake", "CONSUMES"),
            # OCI
            ("oci-vcn-lb", "oci-vm-app", "CONNECTS_TO"),
            ("oci-vm-app", "oci-atp-db", "DEPENDS_ON"),
            ("oci-vm-app", "oci-obj-store", "CONSUMES"),
        ]

        for src, tgt, etype in dep_chains:
            src_n = created_nodes.get(src)
            tgt_n = created_nodes.get(tgt)
            if src_n and tgt_n:
                edge = (
                    db.query(DependencyEdge)
                    .filter(DependencyEdge.source_node_id == src_n.id, DependencyEdge.target_node_id == tgt_n.id)
                    .first()
                )
                if not edge:
                    edge = DependencyEdge(
                        source_node_id=src_n.id,
                        target_node_id=tgt_n.id,
                        edge_type=etype,
                        confidence_score=1.0,
                        cost_allocation_pct=100.0,
                        source_type="NATIVE_DISCOVERY",
                    )
                    db.add(edge)
        db.commit()

        # 7. Budgets across Hierarchies
        budgets_def = [
            ("Global Multi-Cloud Budget", "GLOBAL", "*", 3000.0, 75.0, 95.0, 110.0, 2180.19),
            ("Azure Production Budget", "PROVIDER", "AZURE", 800.0, 75.0, 95.0, 110.0, 696.56),
            ("AWS Core Banking Budget", "PROVIDER", "AWS", 700.0, 75.0, 95.0, 110.0, 601.91),
            ("GCP Data Analytics Budget", "PROVIDER", "GCP", 650.0, 75.0, 95.0, 110.0, 537.70),
            ("OCI Enterprise Billing Budget", "PROVIDER", "OCI", 450.0, 75.0, 95.0, 110.0, 347.82),
        ]
        for bname, stype, sid, amt, wthr, cthr, fthr, cur in budgets_def:
            b = db.query(Budget).filter(Budget.name == bname).first()
            if not b:
                b = Budget(
                    tenant_id=tenant.id,
                    name=bname,
                    scope_type=stype,
                    scope_id=sid,
                    amount=amt,
                    currency="USD",
                    period="MONTHLY",
                    warning_threshold_pct=wthr,
                    critical_threshold_pct=cthr,
                    forecast_threshold_pct=fthr,
                    current_spend=cur,
                    forecasted_spend=round(cur * 1.042, 2),
                    owner_email="finops-director@company.com",
                    alert_emails=["finops-director@company.com", "cloud-governance@company.com"],
                )
                db.add(b)
        db.commit()

        # 8. Realistic Alerts
        alerts_def = [
            ("BUDGET_WARNING", "WARNING", "OPEN", "Azure Spend Approaching Warning Threshold", "Azure monthly spend is at 87.1% of allocated $800.00 budget.", 87.1, 75.0, "%"),
            ("THRESHOLD_DRIFT", "INFO", "OPEN", "AWS EC2 Off-Hours Adherence Normal", "EC2 instance running 24x7 within normal operational parameters.", 24.0, 24.0, "Hours"),
            ("PRICING_UPDATED", "INFO", "ACKNOWLEDGED", "Azure Retail Catalog Refreshed", "Synchronized latest D4s_v5 price point from Azure Retail Prices API.", 0.192, 0.192, "USD"),
        ]
        for atype, sev, st, title, msg, oval, tval, unit in alerts_def:
            al = db.query(Alert).filter(Alert.title == title).first()
            if not al:
                al = Alert(
                    alert_type=atype,
                    severity=sev,
                    status=st,
                    title=title,
                    message=msg,
                    observed_value=oval,
                    threshold_value=tval,
                    unit=unit,
                )
                db.add(al)
        db.commit()

        return tenant
