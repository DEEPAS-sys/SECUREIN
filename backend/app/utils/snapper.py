"""
Snapshot utility for capturing and storing images
"""
import io
import logging
from datetime import datetime
from PIL import Image
import numpy as np
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = logging.getLogger(__name__)


class SnapshotService:
    """Service for managing snapshots"""
    
    def __init__(self):
        self.minio_client = None
        if settings.MINIO_URL:
            self.minio_client = Minio(
                settings.MINIO_URL,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
        except S3Error as e:
            logger.error(f"MinIO bucket error: {e}")
    
    def save_snapshot(self, image: np.ndarray, camera_id: int, alert_id: int) -> str:
        """Save snapshot to object storage"""
        try:
            # Convert numpy array to JPEG
            pil_image = Image.fromarray(image)
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Generate object name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            object_name = f"snapshots/camera_{camera_id}/alert_{alert_id}_{timestamp}.jpg"
            
            # Upload to MinIO
            if self.minio_client:
                self.minio_client.put_object(
                    settings.MINIO_BUCKET_NAME,
                    object_name,
                    img_byte_arr,
                    length=img_byte_arr.getbuffer().nbytes,
                    content_type='image/jpeg'
                )
            
            return object_name
            
        except Exception as e:
            logger.error(f"Snapshot save error: {e}")
            return None
    
    def get_snapshot_url(self, object_name: str, expires: int = 3600) -> str:
        """Get presigned URL for snapshot"""
        try:
            if self.minio_client:
                url = self.minio_client.presigned_get_object(
                    settings.MINIO_BUCKET_NAME,
                    object_name,
                    expires=expires
                )
                return url
        except S3Error as e:
            logger.error(f"Presigned URL error: {e}")
        
        return None


# Singleton instance
snapshot_service = SnapshotService()
