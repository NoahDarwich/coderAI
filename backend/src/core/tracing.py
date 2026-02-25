"""
OpenTelemetry tracing setup.

Gated behind OTEL_ENABLED=true — zero cost when disabled.
Provides auto-instrumentation for FastAPI, SQLAlchemy, and Redis,
plus a helper to create manual spans for LLM calls.
"""
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)

# Sentinel for no-op when tracing is disabled
_tracer_provider = None


def setup_tracing(app) -> None:
    """
    Initialize OpenTelemetry tracing if OTEL_ENABLED is True.

    Auto-instruments FastAPI, SQLAlchemy, and Redis.
    No-op when OTEL_ENABLED is False.
    """
    global _tracer_provider

    if not settings.OTEL_ENABLED:
        logger.debug("OpenTelemetry tracing disabled (OTEL_ENABLED=false)")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
        _tracer_provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(endpoint=f"{settings.OTEL_EXPORTER_ENDPOINT}/v1/traces")
        _tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(_tracer_provider)

        # Auto-instrument
        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument()
        RedisInstrumentor().instrument()

        logger.info("OpenTelemetry tracing initialized (service=%s)", settings.OTEL_SERVICE_NAME)

    except ImportError as e:
        logger.warning("OpenTelemetry packages not installed, tracing disabled: %s", e)
    except Exception as e:
        logger.error("Failed to initialize OpenTelemetry tracing: %s", e)


class _NoOpSpan:
    """No-op span for when OpenTelemetry is not installed."""

    def set_attribute(self, key: str, value) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class _NoOpTracer:
    """No-op tracer for when OpenTelemetry is not installed."""

    def start_as_current_span(self, name: str, **kwargs):
        return _NoOpSpan()


def get_tracer(name: str):
    """
    Return an OpenTelemetry tracer.

    When OTEL is disabled or packages are not installed, returns a no-op tracer.
    """
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        return _NoOpTracer()
