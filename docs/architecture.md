# Video Analytics Platform Architecture

## System Overview

The Video Analytics Platform is a distributed system designed for real-time AI-powered video analysis from IP/RTSP cameras.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │   Alerts     │  │    Rules     │          │
│  │   (React)    │  │   (React)    │  │   (React)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/WebSocket
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               FastAPI Backend                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │  Auth    │ │ Cameras  │ │  Rules   │ │ Alerts   │    │   │
│  │  │   API    │ │   API    │ │   API    │ │   API    │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   PostgreSQL   │ │     Redis      │ │  Elasticsearch │
│   (Metadata)   │ │    (Cache)     │ │    (Search)    │
└────────────────┘ └────────────────┘ └────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
┌────────────────────────────────────────────────────────────────┐
│                     Processing Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Ingest     │  │  Inference   │  │     Rule     │         │
│  │   Worker     │  │   Worker     │  │    Engine    │         │
│  │  (FFmpeg)    │  │   (GPU)      │  │   (Python)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   RabbitMQ     │ │     MinIO      │ │   RTSP Cams    │
│  (Messages)    │ │   (Storage)    │ │   (Streams)    │
└────────────────┘ └────────────────┘ └────────────────┘
```

## Component Details

### Frontend
- **Technology**: React 18 + TypeScript + Tailwind CSS
- **State Management**: React Query for server state
- **Real-time**: WebSocket for live alerts
- **Video Player**: Video.js for HLS playback

### Backend API
- **Framework**: FastAPI (async Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with role-based access control
- **Caching**: Redis for session and query caching
- **Search**: Elasticsearch for fast alert queries

### Processing Workers

#### Ingest Worker
- Consumes RTSP streams using FFmpeg
- Samples frames at configurable FPS (default 5fps)
- Publishes frames to message queue (RabbitMQ)

#### Inference Worker
- GPU-accelerated AI inference
- Supports multiple models:
  - Object detection (YOLOv8, MobileNet)
  - Face recognition (FaceNet)
  - License plate recognition (ALPR)
  - Object tracking (DeepSORT)
- Batched processing for efficiency
- Publishes detections to message queue

#### Rule Engine
- Evaluates detection rules in real-time
- Supports spatial rules (zone entry/exit)
- Supports temporal rules (dwell time)
- Maintains state for stateful rules
- Triggers alerts on rule matches

### Storage

#### PostgreSQL
- Stores metadata: users, cameras, rules, alerts, detections
- ACID transactions for data consistency
- Connection pooling for performance

#### Redis
- Caches frequently accessed data
- Stores session tokens
- Message queue for frame distribution
- Pub/sub for real-time events

#### MinIO (S3-compatible)
- Stores snapshots (JPEG images)
- Stores video clips (MP4/HLS segments)
- Provides presigned URLs for secure access

#### Elasticsearch
- Indexes alerts and detections
- Fast full-text and range queries
- Aggregations for analytics

## Data Flow

### Frame Processing Pipeline

1. **Camera → Ingest Worker**
   - FFmpeg connects to RTSP stream
   - Decodes video and samples frames
   - Encodes frames as JPEG
   - Publishes to frame queue

2. **Frame Queue → Inference Worker**
   - Worker pulls batch of frames
   - Preprocesses for model input
   - Runs GPU inference
   - Publishes detection results

3. **Detection Queue → Rule Engine**
   - Evaluates rules against detections
   - Maintains state for stateful rules
   - Triggers alerts on matches

4. **Alert → Alert Service**
   - Creates database record
   - Saves snapshot to MinIO
   - Generates video clip
   - Sends WebSocket notification
   - Indexes in Elasticsearch

### API Request Flow

1. **Client → API Gateway**
   - JWT authentication
   - Rate limiting
   - Request validation

2. **API → Database**
   - Query/update metadata
   - Transaction management

3. **API → Cache**
   - Check cache first
   - Update cache on writes

4. **API → Client**
   - JSON response
   - Presigned URLs for media

## Scalability

### Horizontal Scaling
- **API**: Multiple replicas behind load balancer
- **Inference Workers**: Scale based on GPU capacity
- **Ingest Workers**: One per camera or camera group

### Vertical Scaling
- **Database**: Read replicas for queries
- **Redis**: Cluster mode for high availability
- **GPU**: Multiple GPUs per worker

### Performance Targets
- **Throughput**: 30 FPS aggregate across N cameras
- **Latency**: <100ms inference per frame
- **Capacity**: 50+ cameras per inference worker (GPU)
- **Uptime**: 99.9% availability

## Security

### Authentication & Authorization
- JWT tokens (15min access, 7d refresh)
- Role-based access control (admin, operator, viewer)
- Password hashing with bcrypt
- Encrypted RTSP credentials

### Network Security
- HTTPS only in production
- CORS policy configured
- Rate limiting on API endpoints
- WebSocket authentication via token

### Data Security
- Database field encryption for sensitive data
- Presigned URLs with expiration
- Audit logs for all operations
- Data retention policies

## Monitoring & Observability

### Metrics (Prometheus)
- Inference latency and throughput
- Queue depths
- Camera online/offline status
- Alert generation rate
- API request rate and latency

### Logs (ELK Stack)
- Structured JSON logs
- Centralized log aggregation
- Error tracking and alerting

### Dashboards (Grafana)
- System health overview
- Per-camera metrics
- Alert analytics
- GPU utilization

## Deployment

### Local Development
- Docker Compose with all services
- Hot reload for code changes
- Sample data and camera simulator

### Production (Kubernetes)
- Helm charts for easy deployment
- Autoscaling based on metrics
- Rolling updates
- Health checks and self-healing
- Persistent volumes for data

### Cloud Deployment
- AWS/GCP/Azure compatible
- Terraform for infrastructure
- Managed services option (RDS, ElastiCache, S3)
- Multi-region support

## Future Enhancements

1. **Advanced Analytics**
   - Heat maps
   - People counting
   - Queue analytics
   - Behavior analysis

2. **Edge Deployment**
   - Run inference on edge devices
   - Reduce bandwidth usage
   - Lower latency

3. **Custom Model Training**
   - UI for model training
   - Active learning
   - Model versioning

4. **Integrations**
   - VMS platforms (Milestone, Genetec)
   - Access control systems
   - Building management systems
   - External alerting (Slack, PagerDuty)

5. **Mobile App**
   - iOS and Android apps
   - Push notifications
   - Live view and playback
   - Alert management
