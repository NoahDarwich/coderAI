"""
Token-bucket rate limiter using Redis INCR with TTL.

Provides per-project rate limiting for LLM API calls.
"""
import logging
import time
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, project_id: UUID, retry_after: float):
        self.project_id = project_id
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for project {project_id}. "
            f"Retry after {retry_after:.1f}s"
        )


class RateLimiter:
    """
    Redis-based token bucket rate limiter.

    Uses INCR + EXPIRE for a simple sliding window approach.
    """

    def __init__(
        self,
        redis,
        max_calls: int = 10,
        period_seconds: int = 60,
        key_prefix: str = "ratelimit:llm",
    ):
        """
        Args:
            redis: Redis connection
            max_calls: Maximum calls allowed per period
            period_seconds: Window period in seconds
            key_prefix: Redis key prefix
        """
        self.redis = redis
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.key_prefix = key_prefix

    def _key(self, project_id: UUID) -> str:
        """Build Redis key for project."""
        return f"{self.key_prefix}:{project_id}"

    async def check(self, project_id: UUID) -> bool:
        """
        Check if a call is allowed under the rate limit.

        Returns True if allowed, raises RateLimitExceeded if not.
        """
        key = self._key(project_id)

        # Increment counter
        current = await self.redis.incr(key)

        # Set TTL on first call in window
        if current == 1:
            await self.redis.expire(key, self.period_seconds)

        if current > self.max_calls:
            # Get TTL to know when to retry
            ttl = await self.redis.ttl(key)
            raise RateLimitExceeded(
                project_id=project_id,
                retry_after=float(max(ttl, 1)),
            )

        return True

    async def get_remaining(self, project_id: UUID) -> int:
        """Get remaining calls in current window."""
        key = self._key(project_id)
        current = await self.redis.get(key)
        if current is None:
            return self.max_calls
        return max(0, self.max_calls - int(current))

    async def reset(self, project_id: UUID) -> None:
        """Reset rate limit for a project."""
        key = self._key(project_id)
        await self.redis.delete(key)


# Module-level singleton, initialized on first use
_rate_limiter: Optional[RateLimiter] = None


async def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        from src.core.redis import get_redis
        from src.core.config import settings

        redis = await get_redis()
        _rate_limiter = RateLimiter(
            redis=redis,
            max_calls=settings.LLM_RATE_LIMIT_CALLS,
            period_seconds=settings.LLM_RATE_LIMIT_PERIOD,
        )
    return _rate_limiter
