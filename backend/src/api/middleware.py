"""
FastAPI middleware for CORS, error handling, and logging.
"""
import logging
from typing import Callable

from fastapi import Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


def add_cors_middleware(app):
    """
    Add CORS middleware to the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    from src.core.config import settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors and converting them to RFC 7807 Problem Details format.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except ValueError as exc:
            # Validation errors
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "type": "https://api.example.com/errors/validation",
                    "title": "Validation Error",
                    "status": 422,
                    "detail": str(exc),
                    "instance": str(request.url.path),
                },
            )
        except Exception as exc:
            # Internal server errors
            logger.exception("Unhandled exception occurred")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "type": "https://api.example.com/errors/internal-server-error",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred",
                    "instance": str(request.url.path),
                },
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
