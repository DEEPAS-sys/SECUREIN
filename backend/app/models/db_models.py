"""
Database models for the video analytics platform.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    """User roles enum."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class CameraStatus(str, enum.Enum):
    """Camera status enum."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    CONNECTING = "connecting"


class RuleType(str, enum.Enum):
    """Rule type enum."""
    ZONE_ENTRY = "zone_entry"
    ZONE_EXIT = "zone_exit"
    DWELL_TIME = "dwell_time"
    OBJECT_COUNT = "object_count"
    LINE_CROSSING = "line_crossing"


class EventType(str, enum.Enum):
    """Event type enum."""
    DETECTION = "detection"
    ALERT = "alert"
    SYSTEM = "system"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class Camera(Base):
    """Camera model."""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    rtsp_url = Column(String(500), nullable=False)
    onvif_url = Column(String(500))
    site = Column(String(100))
    username = Column(String(100))
    password_encrypted = Column(String(500))
    fps = Column(Integer, default=25)
    resolution = Column(String(20), default="1920x1080")
    enabled = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(CameraStatus), default=CameraStatus.OFFLINE, nullable=False)
    last_seen = Column(DateTime(timezone=True))
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    rules = relationship("Rule", back_populates="camera", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="camera", cascade="all, delete-orphan")


class ModelVersion(Base):
    """Model version tracking."""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # detector, face_recog, lpr, tracker
    path = Column(String(500), nullable=False)
    framework = Column(String(50))  # pytorch, onnx, tensorrt
    metadata = Column(JSON, default={})
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Rule(Base):
    """Detection rule model."""
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    rule_type = Column(Enum(RuleType), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Rule configuration (JSON)
    config = Column(JSON, nullable=False)
    # Example config:
    # {
    #   "zone": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],  # polygon points
    #   "object_types": ["person", "vehicle"],
    #   "threshold": 0.5,
    #   "dwell_time_seconds": 10,
    #   "count_threshold": 5,
    #   "schedule": {"start": "08:00", "end": "18:00"}
    # }
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    camera = relationship("Camera", back_populates="rules")
    events = relationship("Event", back_populates="rule")


class Event(Base):
    """Event/Alert model."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rules.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Media references
    snapshot_path = Column(String(500))
    clip_path = Column(String(500))
    
    # Event metadata
    metadata = Column(JSON, default={})
    # Example metadata:
    # {
    #   "object_type": "person",
    #   "confidence": 0.95,
    #   "track_id": "T123",
    #   "bbox": [x1, y1, x2, y2]
    # }
    
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    acknowledged_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    camera = relationship("Camera", back_populates="events")
    rule = relationship("Rule", back_populates="events")
    detections = relationship("Detection", back_populates="event", cascade="all, delete-orphan")


class Detection(Base):
    """Detection model - individual object detections."""
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    
    object_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False)  # [x1, y1, x2, y2]
    track_id = Column(String(50), index=True)
    
    # Additional metadata
    metadata = Column(JSON, default={})
    # Can include: embedding, face_id, plate_number, etc.
    
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    event = relationship("Event", back_populates="detections")


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(50))
    details = Column(JSON, default={})
    ip_address = Column(String(50))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
