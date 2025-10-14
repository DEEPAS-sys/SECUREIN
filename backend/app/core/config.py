from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "VideoAnalyticsPlatform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # Database
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "video_analytics"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres123"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres123@postgres:5432/video_analytics"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://admin:admin123@rabbitmq:5672/"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    
    # MinIO
    MINIO_URL: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "video-analytics"
    MINIO_SECURE: bool = False
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    RATE_LIMIT_PER_MINUTE: int = 60
    BCRYPT_ROUNDS: int = 12
    
    # Inference
    INFERENCE_DEVICE: str = "cuda"
    INFERENCE_BATCH_SIZE: int = 4
    MODEL_PATH: str = "/app/models"
    
    # Stream Processing
    FRAME_SAMPLING_FPS: int = 5
    FRAME_QUEUE_MAX_SIZE: int = 1000
    STREAM_BUFFER_SECONDS: int = 30
    
    # Camera
    CAMERA_CONNECTION_TIMEOUT: int = 10
    CAMERA_PROBE_TIMEOUT: int = 5
    
    # Alerts
    ALERT_SNAPSHOT_ENABLED: bool = True
    ALERT_CLIP_ENABLED: bool = True
    ALERT_CLIP_DURATION: int = 10
    ALERT_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
