from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.db_models import Alert, Detection
from app.models.pydantic_schemas import AlertResponse, AlertAcknowledge
from app.core.security import get_current_user, require_role
import json

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    camera_id: Optional[int] = None,
    event_type: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List alerts with filters"""
    
    query = select(Alert)
    
    conditions = []
    if camera_id:
        conditions.append(Alert.camera_id == camera_id)
    if event_type:
        conditions.append(Alert.event_type == event_type)
    if acknowledged is not None:
        conditions.append(Alert.acknowledged == acknowledged)
    if start_date:
        conditions.append(Alert.timestamp >= start_date)
    if end_date:
        conditions.append(Alert.timestamp <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Alert.timestamp.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alert details including detections"""
    
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Get detections
    det_result = await db.execute(
        select(Detection).where(Detection.alert_id == alert_id)
    )
    detections = det_result.scalars().all()
    
    # Construct response
    alert_dict = {
        "id": alert.id,
        "camera_id": alert.camera_id,
        "rule_id": alert.rule_id,
        "event_type": alert.event_type,
        "timestamp": alert.timestamp,
        "snapshot_path": alert.snapshot_path,
        "clip_path": alert.clip_path,
        "metadata": alert.metadata,
        "acknowledged": alert.acknowledged,
        "acknowledged_by": alert.acknowledged_by,
        "acknowledged_at": alert.acknowledged_at,
        "detections": [
            {
                "object_type": d.object_type,
                "confidence": d.confidence,
                "bbox": d.bbox,
                "track_id": d.track_id,
                "attributes": d.attributes
            }
            for d in detections
        ]
    }
    
    return alert_dict


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge an alert"""
    
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.acknowledged = True
    alert.acknowledged_by = int(current_user["id"])
    alert.acknowledged_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
