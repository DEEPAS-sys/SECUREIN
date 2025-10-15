"""
Stream management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set
import logging
import json
import asyncio

from app.models.pydantic_schemas import StreamRequest, StreamResponse
from app.models.db_models import Camera
from app.core.security import get_current_user
from app.db.session import get_db
from app.services.stream_service import StreamService

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast(self, message: str):
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")


manager = ConnectionManager()


@router.post("/{camera_id}/hls", response_model=StreamResponse)
async def create_hls_stream(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create or refresh HLS stream for a camera."""
    from sqlalchemy import select
    
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    stream_service = StreamService()
    stream_info = await stream_service.create_hls_stream(camera)
    
    return stream_info


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    # Extract token from query params
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                # Echo back for heartbeat
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": str(asyncio.get_event_loop().time())}))
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


async def broadcast_alert(alert_data: dict):
    """Helper function to broadcast alerts to all connected clients."""
    message = json.dumps({
        "type": "alert",
        "data": alert_data
    })
    await manager.broadcast(message)
