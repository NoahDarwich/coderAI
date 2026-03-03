"""
FastAPI application initialization and configuration.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import ErrorHandlerMiddleware, LoggingMiddleware
from src.api.routes import auth, copilot, documents, exports, processing, projects, variables, websocket, wizard
from src.core.config import settings
from src.core.logging import setup_logging

logger = logging.getLogger(__name__)

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    from src.core.redis import get_redis
    from src.core.job_subscriber import start_subscriber
    await get_redis()
    start_subscriber()
    logger.info("Redis connection and job subscriber initialized")

    from src.core.tracing import setup_tracing
    setup_tracing(app)

    # In DEBUG mode, create all tables from models (bypasses PG-specific migrations)
    if settings.DEBUG:
        from src.core.database import Base, _get_engine
        # Import all models so they register with Base.metadata
        import src.models.user  # noqa
        import src.models.project  # noqa
        import src.models.document  # noqa
        import src.models.variable  # noqa
        import src.models.processing_job  # noqa
        import src.models.extraction  # noqa
        async with _get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created from models (debug mode)")

    # Seed dev user when DEBUG=True (skips auth for local development)
    if settings.DEBUG:
        from sqlalchemy import select
        from src.core.database import AsyncSessionLocal
        from src.models.user import User
        from src.core.security import get_password_hash
        from src.api.dependencies import DEV_USER_EMAIL
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == DEV_USER_EMAIL))
            if not result.scalar_one_or_none():
                session.add(User(
                    email=DEV_USER_EMAIL,
                    hashed_password=get_password_hash("dev"),
                    is_active=True,
                ))
                await session.commit()
                logger.info("Dev user seeded: %s", DEV_USER_EMAIL)

    yield

    # Shutdown
    from src.core.redis import close_redis
    from src.core.database import close_db
    from src.core.job_subscriber import stop_subscriber
    await stop_subscriber()
    await close_redis()
    await close_db()
    logger.info("Connections closed")


# Create FastAPI app
app = FastAPI(
    title="Data Extraction API",
    description="Backend API for LLM-powered document data extraction workflow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(variables.router)
app.include_router(documents.router)
app.include_router(processing.router)
app.include_router(exports.router)
app.include_router(copilot.router)
app.include_router(websocket.router)
app.include_router(wizard.router)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    from src.core.metrics import metrics_endpoint
    return await metrics_endpoint()


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "message": "Data Extraction API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/health/live")
async def liveness():
    """Liveness probe — returns 200 if process is running."""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    """
    Readiness probe — checks DB and Redis connectivity.
    Returns 200 if all dependencies are reachable, 503 otherwise.
    """
    from fastapi.responses import JSONResponse
    from src.core.database import _get_engine
    from sqlalchemy import text

    checks = {}

    # Check database
    try:
        engine = _get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Check Redis
    try:
        from src.core.redis import get_redis
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503

    return JSONResponse(
        content={"status": "ready" if all_ok else "not_ready", "checks": checks},
        status_code=status_code,
    )
