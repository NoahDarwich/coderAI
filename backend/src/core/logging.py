"""
Logging configuration with structured JSON logging support.

This module provides centralized logging configuration for the application,
with support for both development (pretty) and production (JSON) formats.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from .config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds standard fields to all log records.
    
    Adds:
    - timestamp: ISO 8601 formatted timestamp
    - service: Application service name
    - environment: Deployment environment (dev/staging/prod)
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add service name and environment
        log_record['service'] = 'data-extraction-api'
        log_record['environment'] = settings.ENVIRONMENT
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add module and function info
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        
        # Add line number for debugging
        if settings.DEBUG:
            log_record['line'] = record.lineno


def setup_logging() -> None:
    """
    Configure application logging.
    
    Sets up logging with the appropriate formatter based on environment:
    - Development: Human-readable console output
    - Production: Structured JSON logging for log aggregation
    
    Log levels are determined by settings.LOG_LEVEL.
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Choose formatter based on environment
    if settings.DEBUG:
        # Development: Pretty console logging
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Production: JSON logging
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "debug_mode": settings.DEBUG,
            "environment": settings.ENVIRONMENT,
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Processing started", extra={"project_id": project_id})
    """
    return logging.getLogger(name)
