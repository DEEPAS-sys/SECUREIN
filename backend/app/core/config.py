"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Video Analytics Platform"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://videoadmin:videopass123@localhost:5432/videodb"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672"
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "video-analytics"
    MINIO_SECURE: bool = False
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key-at-least-32-characters-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # GPU Configuration
    GPU_ENABLED: bool = True
    INFERENCE_BATCH_SIZE: int = 8
    SAMPLING_RATE_FPS: int = 5
    
    # Model Configuration
    MODEL_PATH: str = "/app/models"
    DETECTOR_MODEL: str = "yolov8n"
    FACE_MODEL: str = "facenet"
    LPR_MODEL: str = "alpr"
    
    # Camera Configuration
    DEFAULT_CAMERA_FPS: int = 25
    DEFAULT_CAMERA_RESOLUTION: str = "1920x1080"
    RING_BUFFER_SECONDS: int = 30
    
    # Alert Configuration
    ALERT_RETENTION_DAYS: int = 90
    CLIP_DURATION_SECONDS: int = 10
    
    # Performance
    MAX_WORKERS: int = 4
    QUEUE_MAX_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            """Parse environment variables."""
            if field_name in ["CORS_ORIGINS", "ALLOWED_HOSTS"]:
                try:
                    return json.loads(raw_val)
                except json.JSONDecodeError:
                    return raw_val.split(",")
            return raw_val


settings = Settings()
