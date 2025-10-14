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


class EventType(str, Enum):
    OBJECT_DETECTED = "object_detected"
    ZONE_ENTRY = "zone_entry"
    ZONE_EXIT = "zone_exit"
    DWELL_TIME = "dwell_time"
    FACE_RECOGNIZED = "face_recognized"
    LICENSE_PLATE = "license_plate"
    ANOMALY = "anomaly"


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# Camera Schemas
class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    onvif_url: Optional[str] = None
    site: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    fps: int = Field(default=5, ge=1, le=30)
    resolution: str = "1920x1080"
    enabled: bool = True


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    onvif_url: Optional[str] = None
    site: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    fps: Optional[int] = Field(None, ge=1, le=30)
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
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CameraStatus(BaseModel):
    camera_id: int
    status: CameraStatus
    last_seen: Optional[datetime]
    fps: Optional[float]
    errors: Optional[List[str]]


# Rule Schemas
class RuleBase(BaseModel):
    camera_id: int
    name: str
    type: str
    rule_config: Dict[str, Any]
    enabled: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class RuleResponse(BaseModel):
    id: int
    camera_id: int
    name: str
    type: str
    rule_config: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Alert Schemas
class DetectionSchema(BaseModel):
    object_type: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    track_id: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class AlertBase(BaseModel):
    camera_id: int
    rule_id: Optional[int] = None
    event_type: EventType
    metadata: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    snapshot_path: Optional[str] = None
    clip_path: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    camera_id: int
    rule_id: Optional[int]
    event_type: EventType
    timestamp: datetime
    snapshot_path: Optional[str]
    clip_path: Optional[str]
    metadata: Optional[Dict[str, Any]]
    acknowledged: bool
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]
    detections: List[DetectionSchema] = []
    
    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    user_id: int


# Stream Schemas
class StreamCreate(BaseModel):
    camera_id: int
    format: str = "hls"  # hls, webrtc


class StreamResponse(BaseModel):
    camera_id: int
    url: str
    format: str
    expires_at: Optional[datetime]


# Pagination
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


# WebSocket Messages
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
