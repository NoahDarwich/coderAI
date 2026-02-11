"""
WebSocket connection manager for real-time job progress updates.
"""
import json
import logging
from collections import defaultdict
from typing import Any, Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per job ID."""

    def __init__(self):
        self._connections: Dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection for a job."""
        await websocket.accept()
        self._connections[job_id].append(websocket)
        logger.info(f"WebSocket connected for job {job_id} (total: {len(self._connections[job_id])})")

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if job_id in self._connections:
            self._connections[job_id] = [
                ws for ws in self._connections[job_id] if ws is not websocket
            ]
            if not self._connections[job_id]:
                del self._connections[job_id]
        logger.info(f"WebSocket disconnected for job {job_id}")

    async def broadcast_to_job(self, job_id: str, event: Dict[str, Any]) -> None:
        """Broadcast an event to all WebSocket connections for a job."""
        if job_id not in self._connections:
            return

        message = json.dumps(event)
        dead_connections = []

        for websocket in self._connections[job_id]:
            try:
                await websocket.send_text(message)
            except Exception:
                dead_connections.append(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(job_id, ws)

    @property
    def active_connections(self) -> int:
        """Total number of active WebSocket connections."""
        return sum(len(conns) for conns in self._connections.values())


# Singleton instance
manager = ConnectionManager()
