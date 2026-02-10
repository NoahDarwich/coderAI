"""
FastAPI application initialization and configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import ErrorHandlerMiddleware, LoggingMiddleware
from src.api.routes import documents, exports, processing, projects, variables
from src.core.config import settings
from src.core.logging import setup_logging

# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Data Extraction API",
    description="Backend API for LLM-powered document data extraction workflow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
app.include_router(projects.router)
app.include_router(variables.router)
app.include_router(documents.router)
app.include_router(processing.router)
app.include_router(exports.router)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
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
