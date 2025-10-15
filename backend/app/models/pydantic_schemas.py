"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    CONNECTING = "connecting"


class RuleType(str, Enum):
    ZONE_ENTRY = "zone_entry"
    ZONE_EXIT = "zone_exit"
    DWELL_TIME = "dwell_time"
    OBJECT_COUNT = "object_count"
    LINE_CROSSING = "line_crossing"


class EventType(str, Enum):
    DETECTION = "detection"
    ALERT = "alert"
    SYSTEM = "system"


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# Camera Schemas
class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rtsp_url: str = Field(..., min_length=1)
    onvif_url: Optional[str] = None
    site: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    fps: int = Field(default=25, ge=1, le=60)
    resolution: str = "1920x1080"


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rtsp_url: Optional[str] = None
    onvif_url: Optional[str] = None
    site: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    fps: Optional[int] = Field(None, ge=1, le=60)
    resolution: Optional[str] = None
    enabled: Optional[bool] = None


class CameraResponse(BaseModel):
    id: int
    name: str
    rtsp_url: str
    onvif_url: Optional[str]
    site: Optional[str]
    fps: int
    resolution: str
    enabled: bool
    status: CameraStatus
    last_seen: Optional[datetime]
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CameraStatusResponse(BaseModel):
    camera_id: int
    status: CameraStatus
    last_seen: Optional[datetime]
    connectivity: bool
    last_frame_timestamp: Optional[datetime]
    error_message: Optional[str] = None


# Rule Schemas
class RuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rule_type: RuleType
    config: Dict[str, Any]
    enabled: bool = True


class RuleCreate(RuleBase):
    camera_id: int


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_type: Optional[RuleType] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class RuleResponse(RuleBase):
    id: int
    camera_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Event/Alert Schemas
class DetectionSchema(BaseModel):
    object_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: List[float]  # [x1, y1, x2, y2]
    track_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class EventBase(BaseModel):
    camera_id: int
    event_type: EventType
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class EventCreate(EventBase):
    rule_id: Optional[int] = None
    snapshot_path: Optional[str] = None
    clip_path: Optional[str] = None


class EventResponse(EventBase):
    id: int
    rule_id: Optional[int]
    snapshot_path: Optional[str]
    clip_path: Optional[str]
    snapshot_url: Optional[str] = None
    clip_url: Optional[str] = None
    acknowledged: bool
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    detections: List[DetectionSchema] = []
    
    class Config:
        from_attributes = True


class EventAcknowledge(BaseModel):
    acknowledged: bool


# Stream Schemas
class StreamRequest(BaseModel):
    camera_id: int


class StreamResponse(BaseModel):
    camera_id: int
    hls_url: str
    manifest_url: str


# Health Schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]


# Pagination
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
