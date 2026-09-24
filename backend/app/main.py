"""
CloudScope Backend Application Entrypoint
FastAPI application setup with structured logging, CORS, correlation tracing, and global error handling.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import configure_logging, logger
from app.core.database import engine, Base, SessionLocal
from app.core.middleware import CorrelationIdMiddleware, global_exception_handler
from app.api.v1.api import api_v1_router
from app.connectors.demo_adapter import DemoDataGenerator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Configure logging and initialize database
    configure_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed demo data if enabled and DB empty
    if settings.DEMO_MODE_ENABLED:
        db = SessionLocal()
        try:
            from app.models.hierarchy import ResourceNode
            if db.query(ResourceNode).count() == 0:
                logger.info("Empty database detected; seeding multi-cloud demo estate...")
                DemoDataGenerator.seed_complete_demo_estate(db)
                logger.info("Multi-cloud demo estate successfully initialized.")
        finally:
            db.close()

    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Cloud Service Inventory, Pricing Intelligence, and Cost Governance Platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Global Exception Handler (Rules 2.3 & 2.4)
app.add_exception_handler(Exception, global_exception_handler)

# Correlation ID Distributed Tracing Middleware (Rule 4.2)
app.add_middleware(CorrelationIdMiddleware)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time-Ms"],
)

# Mount API v1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    """Liveness and readiness probe for Docker / Kubernetes."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo_mode": settings.DEMO_MODE_ENABLED,
    }
