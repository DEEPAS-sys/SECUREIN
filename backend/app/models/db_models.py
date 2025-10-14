from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.session import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class CameraStatus(str, enum.Enum):
    """Camera status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    CONNECTING = "connecting"


class EventType(str, enum.Enum):
    """Event type enumeration"""
    OBJECT_DETECTED = "object_detected"
    ZONE_ENTRY = "zone_entry"
    ZONE_EXIT = "zone_exit"
    DWELL_TIME = "dwell_time"
    FACE_RECOGNIZED = "face_recognized"
    LICENSE_PLATE = "license_plate"
    ANOMALY = "anomaly"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")


class Camera(Base):
    """Camera model"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    rtsp_url = Column(String(500), nullable=False)
    onvif_url = Column(String(500))
    site = Column(String(255))
    username = Column(String(100))
    password = Column(String(255))  # Encrypted
    fps = Column(Integer, default=5)
    resolution = Column(String(50), default="1920x1080")
    enabled = Column(Boolean, default=True)
    status = Column(Enum(CameraStatus), default=CameraStatus.OFFLINE)
    last_seen = Column(DateTime(timezone=True))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    rules = relationship("Rule", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")


class Model(Base):
    """AI Model model"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)  # detector, face_recog, lpr, etc.
    path = Column(String(500), nullable=False)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Rule(Base):
    """Rule model"""
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # zone_entry, zone_exit, dwell_time, etc.
    rule_config = Column(JSON, nullable=False)  # Zone geometry, thresholds, etc.
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    camera = relationship("Camera", back_populates="rules")
    alerts = relationship("Alert", back_populates="rule")


class Alert(Base):
    """Alert/Event model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    snapshot_path = Column(String(500))
    clip_path = Column(String(500))
    metadata = Column(JSON)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))
    
    # Relationships
    camera = relationship("Camera", back_populates="alerts")
    rule = relationship("Rule", back_populates="alerts")
    detections = relationship("Detection", back_populates="alert")


class Detection(Base):
    """Detection model"""
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    object_type = Column(String(50), nullable=False, index=True)  # person, car, face, etc.
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=False)  # [x1, y1, x2, y2]
    track_id = Column(String(50))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    attributes = Column(JSON)  # Additional attributes like color, gender, etc.
    
    # Relationships
    alert = relationship("Alert", back_populates="detections")


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(255), nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
