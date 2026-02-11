"""
Redis connection manager for ARQ job queue and pub/sub.
"""
import logging
from typing import Optional

from redis.asyncio import ConnectionPool, Redis

from src.core.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[ConnectionPool] = None
_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get the shared async Redis client."""
    global _pool, _redis
    if _redis is None:
        _pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        _redis = Redis(connection_pool=_pool)
    return _redis


async def get_redis_bytes() -> Redis:
    """Get a Redis client that returns bytes (for pub/sub binary data)."""
    global _pool
    if _pool is None:
        await get_redis()
    return Redis(connection_pool=_pool, decode_responses=False)


async def close_redis() -> None:
    """Close Redis connections and pool."""
    global _pool, _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
    logger.info("Redis connections closed")
