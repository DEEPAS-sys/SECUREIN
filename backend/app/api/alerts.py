"""
Alerts API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
import logging

from app.models.pydantic_schemas import EventResponse, EventAcknowledge
from app.models.db_models import Event, Detection, EventType
from app.core.security import get_current_user
from app.db.session import get_db
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[EventResponse])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    camera_id: Optional[int] = None,
    event_type: Optional[EventType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    acknowledged: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List alerts with optional filters."""
    query = select(Event)
    
    if camera_id:
        query = query.where(Event.camera_id == camera_id)
    
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    if start_time:
        query = query.where(Event.timestamp >= start_time)
    
    if end_time:
        query = query.where(Event.timestamp <= end_time)
    
    if acknowledged is not None:
        query = query.where(Event.acknowledged == acknowledged)
    
    # Order by most recent first
    query = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    # Get presigned URLs for media
    alert_service = AlertService(db)
    events_with_urls = []
    for event in events:
        event_dict = {
            "id": event.id,
            "camera_id": event.camera_id,
            "rule_id": event.rule_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "snapshot_path": event.snapshot_path,
            "clip_path": event.clip_path,
            "metadata": event.metadata,
            "acknowledged": event.acknowledged,
            "acknowledged_by": event.acknowledged_by,
            "acknowledged_at": event.acknowledged_at,
            "created_at": event.created_at,
            "snapshot_url": await alert_service.get_presigned_url(event.snapshot_path) if event.snapshot_path else None,
            "clip_url": await alert_service.get_presigned_url(event.clip_path) if event.clip_path else None,
            "detections": []
        }
        events_with_urls.append(event_dict)
    
    return events_with_urls


@router.get("/{alert_id}", response_model=EventResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific alert by ID."""
    result = await db.execute(
        select(Event)
        .where(Event.id == alert_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Get detections
    detections_result = await db.execute(
        select(Detection).where(Detection.event_id == alert_id)
    )
    detections = detections_result.scalars().all()
    
    # Get presigned URLs
    alert_service = AlertService(db)
    
    return {
        "id": event.id,
        "camera_id": event.camera_id,
        "rule_id": event.rule_id,
        "event_type": event.event_type,
        "timestamp": event.timestamp,
        "snapshot_path": event.snapshot_path,
        "clip_path": event.clip_path,
        "metadata": event.metadata,
        "acknowledged": event.acknowledged,
        "acknowledged_by": event.acknowledged_by,
        "acknowledged_at": event.acknowledged_at,
        "created_at": event.created_at,
        "snapshot_url": await alert_service.get_presigned_url(event.snapshot_path) if event.snapshot_path else None,
        "clip_url": await alert_service.get_presigned_url(event.clip_path) if event.clip_path else None,
        "detections": [
            {
                "object_type": d.object_type,
                "confidence": d.confidence,
                "bbox": d.bbox,
                "track_id": d.track_id,
                "metadata": d.metadata
            }
            for d in detections
        ]
    }


@router.patch("/{alert_id}/acknowledge", response_model=EventResponse)
async def acknowledge_alert(
    alert_id: int,
    acknowledge_data: EventAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge or unacknowledge an alert."""
    result = await db.execute(select(Event).where(Event.id == alert_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    event.acknowledged = acknowledge_data.acknowledged
    if acknowledge_data.acknowledged:
        event.acknowledged_by = int(current_user["sub"])
        event.acknowledged_at = datetime.utcnow()
    else:
        event.acknowledged_by = None
        event.acknowledged_at = None
    
    await db.commit()
    await db.refresh(event)
    
    logger.info(f"Alert {alert_id} acknowledged by user {current_user['username']}")
    
    # Get presigned URLs
    alert_service = AlertService(db)
    
    return {
        "id": event.id,
        "camera_id": event.camera_id,
        "rule_id": event.rule_id,
        "event_type": event.event_type,
        "timestamp": event.timestamp,
        "snapshot_path": event.snapshot_path,
        "clip_path": event.clip_path,
        "metadata": event.metadata,
        "acknowledged": event.acknowledged,
        "acknowledged_by": event.acknowledged_by,
        "acknowledged_at": event.acknowledged_at,
        "created_at": event.created_at,
        "snapshot_url": await alert_service.get_presigned_url(event.snapshot_path) if event.snapshot_path else None,
        "clip_url": await alert_service.get_presigned_url(event.clip_path) if event.clip_path else None,
        "detections": []
    }
