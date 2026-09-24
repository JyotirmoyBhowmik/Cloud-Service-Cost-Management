"""
Pytest Test Fixtures & In-Memory Test Database
"""

import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import Base
from app.connectors.demo_adapter import DemoDataGenerator


@pytest.fixture(scope="session")
def db_engine():
    """In-memory SQLite engine for fast, isolated test execution."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Provides a transactional database session seeded with test data."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    # Seed demo estate
    DemoDataGenerator.seed_complete_demo_estate(session)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
