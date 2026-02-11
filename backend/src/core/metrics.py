"""
Prometheus metrics for observability.

Provides counters and histograms for key operations:
- Document processing
- Extractions
- LLM API calls
- Extraction confidence distribution
"""
from prometheus_client import Counter, Histogram, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


# --- Info ---
app_info = Info("coderai", "coderAI application info")
app_info.info({"version": "1.0.0"})

# --- Counters ---
documents_processed_total = Counter(
    "coderai_documents_processed_total",
    "Total documents processed",
    ["status"],  # success, failed
)

extractions_total = Counter(
    "coderai_extractions_total",
    "Total extractions performed",
    ["status"],  # extracted, flagged, failed
)

llm_calls_total = Counter(
    "coderai_llm_calls_total",
    "Total LLM API calls",
    ["model", "status"],  # success, error, circuit_breaker
)

jobs_total = Counter(
    "coderai_jobs_total",
    "Total processing jobs",
    ["type", "status"],  # sample/full, completed/failed/cancelled
)

# --- Histograms ---
llm_call_duration_seconds = Histogram(
    "coderai_llm_call_duration_seconds",
    "LLM API call duration in seconds",
    ["model"],
    buckets=[0.5, 1, 2, 5, 10, 30, 60],
)

extraction_confidence = Histogram(
    "coderai_extraction_confidence",
    "Extraction confidence score distribution",
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
)

document_processing_duration_seconds = Histogram(
    "coderai_document_processing_duration_seconds",
    "Document processing duration in seconds",
    buckets=[1, 5, 10, 30, 60, 120, 300],
)


async def metrics_endpoint() -> Response:
    """Prometheus metrics endpoint handler."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
