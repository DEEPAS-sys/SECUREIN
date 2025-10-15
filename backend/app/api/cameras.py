"""
Camera management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import logging

from app.models.pydantic_schemas import (
    CameraCreate, CameraUpdate, CameraResponse,
    CameraStatusResponse, PaginatedResponse
)
from app.models.db_models import Camera, CameraStatus
from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app.services.camera_service import CameraService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new camera."""
    # Only admin and operator can create cameras
    if current_user.get("role") not in ["admin", "operator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    camera_service = CameraService(db)
    camera = await camera_service.create_camera(camera_data)
    
    logger.info(f"Camera created: {camera.name} (ID: {camera.id})")
    return camera


@router.get("", response_model=List[CameraResponse])
async def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    site: Optional[str] = None,
    status_filter: Optional[CameraStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all cameras with optional filters."""
    query = select(Camera)
    
    if site:
        query = query.where(Camera.site == site)
    
    if status_filter:
        query = query.where(Camera.status == status_filter)
    
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
    """Get a specific camera by ID."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
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
    current_user: dict = Depends(get_current_user)
):
    """Update a camera."""
    # Only admin and operator can update cameras
    if current_user.get("role") not in ["admin", "operator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Update fields
    update_data = camera_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value:
            # Encrypt password
            setattr(camera, "password_encrypted", value)
        else:
            setattr(camera, field, value)
    
    await db.commit()
    await db.refresh(camera)
    
    logger.info(f"Camera updated: {camera.name} (ID: {camera.id})")
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a camera (admin only)."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    await db.delete(camera)
    await db.commit()
    
    logger.info(f"Camera deleted: {camera.name} (ID: {camera.id})")


@router.get("/{camera_id}/status", response_model=CameraStatusResponse)
async def get_camera_status(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get camera health and connectivity status."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    camera_service = CameraService(db)
    status_info = await camera_service.get_camera_status(camera)
    
    return status_info
