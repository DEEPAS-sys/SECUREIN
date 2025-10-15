"""
Stream service for HLS stream creation and management.
"""
import logging
from typing import Dict

from app.models.db_models import Camera
from app.models.pydantic_schemas import StreamResponse

logger = logging.getLogger(__name__)


class StreamService:
    """Service for video streaming operations."""
    
    def __init__(self):
        self.active_streams: Dict[int, str] = {}
    
    async def create_hls_stream(self, camera: Camera) -> StreamResponse:
        """Create HLS stream for a camera."""
        # In production, this would start FFmpeg process to create HLS segments
        # For now, return mock response
        
        camera_id = camera.id
        
        # Generate stream URLs
        hls_url = f"http://localhost:8000/streams/hls/{camera_id}/index.m3u8"
        manifest_url = f"http://localhost:8000/streams/hls/{camera_id}/manifest.m3u8"
        
        # Store active stream
        self.active_streams[camera_id] = hls_url
        
        logger.info(f"Created HLS stream for camera {camera_id}")
        
        return StreamResponse(
            camera_id=camera_id,
            hls_url=hls_url,
            manifest_url=manifest_url
        )
    
    async def stop_stream(self, camera_id: int):
        """Stop HLS stream for a camera."""
        if camera_id in self.active_streams:
            del self.active_streams[camera_id]
            logger.info(f"Stopped HLS stream for camera {camera_id}")
