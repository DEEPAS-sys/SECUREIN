from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.db.session import get_db
from app.models.db_models import Camera, CameraStatus as DBCameraStatus
from app.models.pydantic_schemas import CameraCreate, CameraUpdate, CameraResponse
from app.core.security import get_current_user, require_role

router = APIRouter()


@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("operator"))
):
    """Add a new camera"""
    
    # Create new camera
    new_camera = Camera(
        name=camera_data.name,
        rtsp_url=camera_data.rtsp_url,
        onvif_url=camera_data.onvif_url,
        site=camera_data.site,
        username=camera_data.username,
        password=camera_data.password,  # TODO: Encrypt in production
        fps=camera_data.fps,
        resolution=camera_data.resolution,
        enabled=camera_data.enabled,
        status=DBCameraStatus.CONNECTING
    )
    
    db.add(new_camera)
    await db.commit()
    await db.refresh(new_camera)
    
    # TODO: Start ingest worker for this camera
    
    return new_camera


@router.get("/", response_model=List[CameraResponse])
async def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    site: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all cameras"""
    
    query = select(Camera)
    
    if site:
        query = query.where(Camera.site == site)
    if enabled is not None:
        query = query.where(Camera.enabled == enabled)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    cameras = result.scalars().all()
    
    return cameras


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get camera details"""
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("operator"))
):
    """Update camera configuration"""
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Update fields
    update_data = camera_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    await db.commit()
    await db.refresh(camera)
    
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """Delete a camera"""
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    await db.delete(camera)
    await db.commit()
    
    return None


@router.get("/{camera_id}/status")
async def get_camera_status(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get camera connection status and health"""
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # TODO: Get actual real-time status from ingest service
    return {
        "camera_id": camera.id,
        "status": camera.status,
        "last_seen": camera.last_seen,
        "fps": None,  # TODO: Get from metrics
        "errors": []
    }
