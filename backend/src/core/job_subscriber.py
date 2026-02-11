"""
Redis pub/sub subscriber that forwards job progress events to WebSocket clients.
"""
import asyncio
import json
import logging

from src.core.websocket import manager

logger = logging.getLogger(__name__)

_subscriber_task = None


async def _subscribe_loop() -> None:
    """Subscribe to job progress Redis channels and forward to WebSocket."""
    from src.core.redis import get_redis_bytes

    redis = await get_redis_bytes()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("job:*:progress")

    logger.info("Job progress subscriber started")

    try:
        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue

            try:
                channel = message["channel"]
                if isinstance(channel, bytes):
                    channel = channel.decode("utf-8")
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                # Extract job_id from channel pattern "job:{job_id}:progress"
                parts = channel.split(":")
                if len(parts) >= 3:
                    job_id = parts[1]
                    event = json.loads(data)
                    await manager.broadcast_to_job(job_id, event)
            except Exception as e:
                logger.error(f"Error processing pub/sub message: {e}")
    except asyncio.CancelledError:
        logger.info("Job progress subscriber cancelled")
    finally:
        await pubsub.punsubscribe("job:*:progress")
        await pubsub.close()


def start_subscriber() -> None:
    """Start the Redis subscriber as a background task."""
    global _subscriber_task
    _subscriber_task = asyncio.create_task(_subscribe_loop())


async def stop_subscriber() -> None:
    """Stop the Redis subscriber."""
    global _subscriber_task
    if _subscriber_task and not _subscriber_task.done():
        _subscriber_task.cancel()
        try:
            await _subscriber_task
        except asyncio.CancelledError:
            pass
        _subscriber_task = None
