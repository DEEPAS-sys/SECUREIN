# API Reference

## Authentication

### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "viewer|operator|admin"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "role": "viewer",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST /api/auth/login
Login and receive JWT tokens.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

## Cameras

### POST /api/cameras
Add a new camera.

**Request Body:**
```json
{
  "name": "Front Entrance",
  "rtsp_url": "rtsp://user:pass@ip:port/stream",
  "onvif_url": "http://ip:port",
  "site": "Main Building",
  "username": "admin",
  "password": "password",
  "fps": 5,
  "resolution": "1920x1080",
  "enabled": true
}
```

**Response:** Camera object

### GET /api/cameras
List all cameras.

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 100, max: 100)
- `site`: Filter by site
- `enabled`: Filter by enabled status

**Response:**
```json
[
  {
    "id": 1,
    "name": "Front Entrance",
    "rtsp_url": "rtsp://...",
    "status": "online",
    "fps": 5,
    "resolution": "1920x1080",
    "enabled": true,
    "last_seen": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET /api/cameras/{camera_id}
Get camera details.

### PUT /api/cameras/{camera_id}
Update camera configuration.

### DELETE /api/cameras/{camera_id}
Delete a camera.

### GET /api/cameras/{camera_id}/status
Get camera connection status and health.

**Response:**
```json
{
  "camera_id": 1,
  "status": "online",
  "last_seen": "2024-01-01T00:00:00Z",
  "fps": 5.2,
  "errors": []
}
```

## Rules

### POST /api/rules
Create a new rule.

**Request Body:**
```json
{
  "camera_id": 1,
  "name": "Zone Entry Detection",
  "type": "zone_entry",
  "rule_config": {
    "zone": [[x1, y1], [x2, y2], [x3, y3]],
    "object_types": ["person", "vehicle"],
    "confidence_threshold": 0.7
  },
  "enabled": true
}
```

### GET /api/rules
List all rules.

**Query Parameters:**
- `camera_id`: Filter by camera
- `enabled`: Filter by enabled status

### GET /api/rules/{rule_id}
Get rule details.

### PUT /api/rules/{rule_id}
Update a rule.

### DELETE /api/rules/{rule_id}
Delete a rule.

## Alerts

### GET /api/alerts
List alerts with filters.

**Query Parameters:**
- `camera_id`: Filter by camera
- `event_type`: Filter by event type
- `acknowledged`: Filter by acknowledgment status
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `skip`: Pagination offset
- `limit`: Results per page

**Response:**
```json
[
  {
    "id": 1,
    "camera_id": 1,
    "rule_id": 1,
    "event_type": "zone_entry",
    "timestamp": "2024-01-01T00:00:00Z",
    "snapshot_path": "snapshots/camera_1/alert_1.jpg",
    "clip_path": "clips/camera_1/alert_1.mp4",
    "metadata": {},
    "acknowledged": false,
    "detections": [
      {
        "object_type": "person",
        "confidence": 0.92,
        "bbox": [100, 200, 300, 400],
        "track_id": "T123"
      }
    ]
  }
]
```

### GET /api/alerts/{alert_id}
Get alert details including detections.

### POST /api/alerts/{alert_id}/acknowledge
Acknowledge an alert.

## Streams

### POST /api/streams/{camera_id}/hls
Create or refresh HLS stream for camera.

**Response:**
```json
{
  "camera_id": 1,
  "url": "/streams/hls/1/playlist.m3u8",
  "format": "hls",
  "expires_at": null
}
```

### GET /api/streams/{camera_id}/snapshot
Get latest snapshot from camera.

## WebSocket

### WS /ws/alerts
Real-time alert notifications.

**Message Format:**
```json
{
  "type": "alert",
  "data": {
    "alert_id": 1,
    "camera_id": 1,
    "event_type": "zone_entry",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "detail": "Error message"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```
