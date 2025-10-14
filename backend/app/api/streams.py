from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.db_models import Camera
from app.models.pydantic_schemas import StreamCreate, StreamResponse
from app.core.security import get_current_user

router = APIRouter()


@router.post("/{camera_id}/hls", response_model=StreamResponse)
async def create_hls_stream(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create or refresh HLS stream for camera"""
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # TODO: Implement actual HLS stream creation
    # For now, return a mock URL
    stream_url = f"/streams/hls/{camera_id}/playlist.m3u8"
    
    return {
        "camera_id": camera_id,
        "url": stream_url,
        "format": "hls",
        "expires_at": None
    }


@router.get("/{camera_id}/snapshot")
async def get_camera_snapshot(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get latest snapshot from camera"""
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # TODO: Get actual snapshot from cache or capture new one
    return {
        "camera_id": camera_id,
        "snapshot_url": f"/snapshots/{camera_id}/latest.jpg",
        "timestamp": None
    }
