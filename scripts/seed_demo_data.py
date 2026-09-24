"""
CLI Script to Seed or Reset Multi-Cloud Demo Estate
Usage: python scripts/seed_demo_data.py
"""

import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import SessionLocal, engine, Base
from app.connectors.demo_adapter import DemoDataGenerator


def main():
    print("Initializing CloudScope database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Seeding Azure, AWS, GCP, and OCI demo estate...")
        tenant = DemoDataGenerator.seed_complete_demo_estate(db)
        print(f"Success! Tenant created: {tenant.name} [{tenant.id}]")
        print("Demo credentials: admin@cloudscope.internal / CloudScope2026!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
