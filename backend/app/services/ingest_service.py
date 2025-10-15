"""
Ingest service for camera stream processing.
"""
import asyncio
import logging
from typing import Optional
import subprocess
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class IngestService:
    """Service for ingesting camera streams."""
    
    def __init__(self):
        self.active_processes = {}
        self.redis_client = None
        self.rabbitmq_connection = None
    
    async def start_ingestion(self, camera_id: int, rtsp_url: str):
        """Start ingesting frames from camera RTSP stream."""
        if camera_id in self.active_processes:
            logger.warning(f"Ingestion already running for camera {camera_id}")
            return
        
        logger.info(f"Starting ingestion for camera {camera_id}")
        
        # FFmpeg command to extract frames
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-vf', f'fps={settings.SAMPLING_RATE_FPS}',
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.active_processes[camera_id] = process
            logger.info(f"Ingestion process started for camera {camera_id}")
            
        except Exception as e:
            logger.error(f"Failed to start ingestion for camera {camera_id}: {e}")
            raise
    
    async def stop_ingestion(self, camera_id: int):
        """Stop ingesting frames from camera."""
        if camera_id not in self.active_processes:
            logger.warning(f"No active ingestion for camera {camera_id}")
            return
        
        process = self.active_processes[camera_id]
        process.terminate()
        
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        del self.active_processes[camera_id]
        logger.info(f"Stopped ingestion for camera {camera_id}")
    
    async def publish_frame(self, camera_id: int, frame_data: bytes, timestamp: str):
        """Publish frame to message queue for inference."""
        message = {
            "camera_id": camera_id,
            "timestamp": timestamp,
            "frame_data": frame_data
        }
        
        # In production, publish to RabbitMQ or Redis stream
        logger.debug(f"Published frame for camera {camera_id}")
