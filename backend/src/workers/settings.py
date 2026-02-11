"""
ARQ worker settings and configuration.
"""
import logging
from arq.connections import RedisSettings

from src.core.config import settings

logger = logging.getLogger(__name__)


def parse_redis_url(url: str) -> RedisSettings:
    """Parse a Redis URL into ARQ RedisSettings."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
        password=parsed.password,
    )


async def startup(ctx: dict) -> None:
    """Worker startup: initialize DB session factory and services."""
    from src.core.database import _get_session_factory
    ctx["session_factory"] = _get_session_factory()
    logger.info("ARQ worker started")


async def shutdown(ctx: dict) -> None:
    """Worker shutdown: clean up resources."""
    from src.core.database import close_db
    await close_db()
    logger.info("ARQ worker shut down")


class WorkerSettings:
    """ARQ worker settings."""
    functions = [
        "src.workers.extraction_worker.process_extraction_job",
        "src.workers.export_worker.process_export_job",
        "src.workers.refinement_worker.process_refinement_job",
    ]
    redis_settings = parse_redis_url(settings.REDIS_URL)
    max_jobs = settings.ARQ_MAX_JOBS
    job_timeout = settings.ARQ_JOB_TIMEOUT
    on_startup = startup
    on_shutdown = shutdown
