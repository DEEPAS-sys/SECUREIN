# Architecture Overview

## System Architecture

The Video Analytics Platform consists of the following main components:

### 1. Frontend (React + TypeScript)
- **Technology**: React 18, TypeScript, Vite, TailwindCSS
- **Features**:
  - User authentication and role-based access
  - Live camera view grid
  - Real-time alerts feed via WebSocket
  - Rule management with visual zone editor
  - Video playback and search

### 2. Backend API (FastAPI)
- **Technology**: Python 3.11, FastAPI, SQLAlchemy (async)
- **Responsibilities**:
  - RESTful API for CRUD operations
  - JWT-based authentication
  - WebSocket for real-time notifications
  - Business logic and orchestration

### 3. Inference Service
- **Technology**: PyTorch, ONNX Runtime, TensorRT
- **Features**:
  - Object detection (YOLO, Faster R-CNN)
  - Face recognition
  - License plate recognition
  - GPU-accelerated inference with batch processing

### 4. Stream Processing Pipeline
- **Components**:
  - **Ingest Workers**: FFmpeg-based RTSP to frame extraction
  - **Frame Queue**: Redis Streams or RabbitMQ
  - **Inference Workers**: Batch processing of frames
  - **Rule Engine**: Event-driven rule evaluation
  - **Alert Service**: Alert generation and notification

### 5. Data Layer
- **PostgreSQL**: Relational data (users, cameras, rules, alerts)
- **Redis**: Caching and real-time data
- **Elasticsearch**: Fast search and indexing
- **MinIO/S3**: Object storage for snapshots and clips

### 6. Message Broker
- **RabbitMQ/Kafka**: Event streaming and worker coordination

## Data Flow

```
RTSP Camera → Ingest Worker → Frame Queue → Inference Worker → Detection Events
                                                    ↓
                                            Rule Engine
                                                    ↓
                                            Alert Service → WebSocket → Frontend
                                                    ↓
                                            DB + Object Storage
```

## Deployment Patterns

### Development (Docker Compose)
- All services run in containers
- GPU support via nvidia-docker
- Local volumes for development

### Production (Kubernetes)
- Horizontal scaling for inference workers
- Auto-scaling based on queue depth
- Persistent volumes for storage
- LoadBalancer for frontend

## Security Architecture

1. **Authentication**: JWT tokens with refresh mechanism
2. **Authorization**: Role-based access control (Admin, Operator, Viewer)
3. **Encryption**: TLS/SSL for all external communication
4. **Secrets**: Encrypted credentials in database
5. **Audit**: All actions logged to audit trail

## Monitoring and Observability

- **Metrics**: Prometheus for system and application metrics
- **Dashboards**: Grafana for visualization
- **Logging**: Structured logging to ELK stack
- **Tracing**: Distributed tracing (optional with OpenTelemetry)

## Scalability Considerations

1. **Horizontal Scaling**: Inference workers can scale based on load
2. **Database**: Read replicas for high-read workloads
3. **Caching**: Redis for frequently accessed data
4. **CDN**: Static assets and HLS streams
5. **Queue Backpressure**: Frame dropping when system is overloaded
