"""
Alert service for managing alerts and media storage.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging
from typing import Optional

from app.models.db_models import Event
from app.core.config import settings

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.minio_client = None
        self._init_minio()
    
    def _init_minio(self):
        """Initialize MinIO client."""
        try:
            from minio import Minio
            
            self.minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            
            # Ensure bucket exists
            if not self.minio_client.bucket_exists(settings.MINIO_BUCKET):
                self.minio_client.make_bucket(settings.MINIO_BUCKET)
                logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO: {e}")
    
    async def get_presigned_url(self, object_path: Optional[str], expiry: int = 3600) -> Optional[str]:
        """Generate presigned URL for object storage."""
        if not object_path or not self.minio_client:
            return None
        
        try:
            url = self.minio_client.presigned_get_object(
                settings.MINIO_BUCKET,
                object_path,
                expires=timedelta(seconds=expiry)
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {object_path}: {e}")
            return None
    
    async def upload_snapshot(self, camera_id: int, frame_data: bytes, timestamp: datetime) -> str:
        """Upload snapshot to object storage."""
        if not self.minio_client:
            raise Exception("MinIO client not initialized")
        
        # Generate object path
        object_path = f"snapshots/{camera_id}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.isoformat()}.jpg"
        
        try:
            from io import BytesIO
            
            self.minio_client.put_object(
                settings.MINIO_BUCKET,
                object_path,
                BytesIO(frame_data),
                len(frame_data),
                content_type='image/jpeg'
            )
            
            logger.info(f"Uploaded snapshot: {object_path}")
            return object_path
        except Exception as e:
            logger.error(f"Failed to upload snapshot: {e}")
            raise
    
    async def upload_clip(self, camera_id: int, clip_data: bytes, timestamp: datetime) -> str:
        """Upload video clip to object storage."""
        if not self.minio_client:
            raise Exception("MinIO client not initialized")
        
        # Generate object path
        object_path = f"clips/{camera_id}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.isoformat()}.mp4"
        
        try:
            from io import BytesIO
            
            self.minio_client.put_object(
                settings.MINIO_BUCKET,
                object_path,
                BytesIO(clip_data),
                len(clip_data),
                content_type='video/mp4'
            )
            
            logger.info(f"Uploaded clip: {object_path}")
            return object_path
        except Exception as e:
            logger.error(f"Failed to upload clip: {e}")
            raise
