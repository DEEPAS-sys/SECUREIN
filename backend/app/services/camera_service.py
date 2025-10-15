"""
Camera service for camera management and health monitoring.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import subprocess
import logging

from app.models.db_models import Camera, CameraStatus
from app.models.pydantic_schemas import CameraCreate, CameraStatusResponse

logger = logging.getLogger(__name__)


class CameraService:
    """Service for camera operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_camera(self, camera_data: CameraCreate) -> Camera:
        """Create a new camera and validate RTSP connection."""
        # Validate RTSP connection
        is_valid = await self.validate_rtsp(camera_data.rtsp_url)
        
        # Create camera
        camera = Camera(
            name=camera_data.name,
            rtsp_url=camera_data.rtsp_url,
            onvif_url=camera_data.onvif_url,
            site=camera_data.site,
            username=camera_data.username,
            password_encrypted=camera_data.password if camera_data.password else None,
            fps=camera_data.fps,
            resolution=camera_data.resolution,
            status=CameraStatus.ONLINE if is_valid else CameraStatus.ERROR
        )
        
        self.db.add(camera)
        await self.db.commit()
        await self.db.refresh(camera)
        
        return camera
    
    async def validate_rtsp(self, rtsp_url: str, timeout: int = 5) -> bool:
        """Validate RTSP stream connectivity using FFmpeg probe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-rtsp_transport', 'tcp',
                '-i', rtsp_url,
                '-show_entries', 'stream=codec_type',
                '-of', 'default=noprint_wrappers=1'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"RTSP validation failed for {rtsp_url}: {e}")
            return False
    
    async def get_camera_status(self, camera: Camera) -> CameraStatusResponse:
        """Get detailed camera status and health."""
        # Check RTSP connectivity
        is_connected = await self.validate_rtsp(camera.rtsp_url)
        
        return CameraStatusResponse(
            camera_id=camera.id,
            status=camera.status,
            last_seen=camera.last_seen,
            connectivity=is_connected,
            last_frame_timestamp=camera.last_seen,
            error_message=None if is_connected else "Camera not reachable"
        )
    
    async def update_camera_status(self, camera_id: int, status: CameraStatus):
        """Update camera status."""
        from sqlalchemy import select, update
        
        await self.db.execute(
            update(Camera)
            .where(Camera.id == camera_id)
            .values(status=status, last_seen=datetime.utcnow())
        )
        await self.db.commit()
