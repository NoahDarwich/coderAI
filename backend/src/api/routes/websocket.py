"""
WebSocket route for real-time job progress updates.
"""
import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.core.websocket import manager
from src.models.processing_job import ProcessingJob

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress.

    Sends initial job state on connect, then forwards Redis pub/sub events.
    Keep-alive pings every 30 seconds.
    """
    # Verify job exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ProcessingJob).where(ProcessingJob.id == job_id)
        )
        job = result.scalar_one_or_none()

    if not job:
        await websocket.close(code=4004, reason="Job not found")
        return

    await manager.connect(job_id, websocket)

    try:
        # Compute ETA for initial state
        eta_seconds = None
        if job.avg_seconds_per_doc is not None and job.status.value == "PROCESSING":
            docs_done = (job.documents_processed or 0) + (job.documents_failed or 0)
            docs_remaining = len(job.document_ids) - docs_done
            eta_seconds = int(job.avg_seconds_per_doc * docs_remaining) if docs_remaining > 0 else 0

        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "job_id": job_id,
            "status": job.status.value,
            "progress": job.progress,
            "documents_processed": job.documents_processed,
            "documents_failed": job.documents_failed,
            "total_documents": len(job.document_ids),
            "eta_seconds": eta_seconds,
        })

        # Keep-alive loop — also receives client messages (ping/pong)
        while True:
            try:
                # Wait for client message with timeout for keep-alive
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
    finally:
        manager.disconnect(job_id, websocket)
