# Video Analytics Platform (Vaidio-like)

A production-ready, end-to-end AI Video Analytics Platform for real-time object detection, face recognition, license plate recognition (LPR), and anomaly detection from IP/RTSP cameras.

## 🎯 Features

- **Real-time Video Analytics**: Object detection, face recognition, LPR, anomaly detection
- **Camera Management**: Connect to IP/RTSP cameras with ONVIF support
- **Rule Engine**: User-defined rules with zone geometry, object types, and thresholds
- **Alert System**: Real-time alerts with stored clips and snapshots
- **Live Dashboard**: Multi-camera live view, alerts feed, search, and configuration
- **Scalable Architecture**: GPU-accelerated inference with horizontal scaling
- **Production Ready**: JWT auth, role-based access, rate limiting, monitoring

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  React + TypeScript + Tailwind
│   (Dashboard)   │  WebSocket for real-time alerts
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Backend API   │  FastAPI + PostgreSQL
│   (FastAPI)     │  JWT Auth, RBAC
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ↓         ↓          ↓          ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Ingest │ │Inference│ │ Rule   │ │ Alert  │
│ Worker │ │ Worker  │ │ Engine │ │ Service│
└────────┘ └────────┘ └────────┘ └────────┘
    │         │          │          │
    └─────────┴──────────┴──────────┘
              │
         ┌────┴────┬──────────┬──────────┐
         ↓         ↓          ↓          ↓
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │RabbitMQ│ │ Redis  │ │ MinIO  │ │Elastic │
    │        │ │        │ │   S3   │ │ Search │
    └────────┘ └────────┘ └────────┘ └────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA Docker runtime (for GPU support)
- Python 3.11+
- Node.js 18+

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/DEEPAS-sys/SECUREIN.git
cd SECUREIN
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
./scripts/setup_db.sh
```

5. **Load demo data (optional)**
```bash
./scripts/load_demo_data.sh
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001

### Default Credentials
- Username: `admin`
- Password: `admin123`

## 📋 Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/videodb` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `RABBITMQ_URL` | RabbitMQ connection string | `amqp://guest:guest@localhost:5672` |
| `MINIO_URL` | MinIO/S3 endpoint | `localhost:9000` |
| `ELASTICSEARCH_URL` | Elasticsearch endpoint | `http://localhost:9200` |
| `SECRET_KEY` | JWT secret key | (generate random) |
| `GPU_ENABLED` | Enable GPU acceleration | `true` |
| `INFERENCE_BATCH_SIZE` | Batch size for inference | `8` |
| `SAMPLING_RATE_FPS` | Frame sampling rate | `5` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000/ws` |

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
./scripts/run_integration_tests.sh
```

### End-to-End Tests
```bash
cd frontend
npx playwright test
```

## 📦 Deployment

### Docker Compose (Local/Dev)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
# Using kubectl
kubectl apply -f infra/k8s/

# Using Helm
helm install video-analytics infra/helm/video-analytics
```

### GPU Support
Ensure NVIDIA Container Toolkit is installed:
```bash
# Install nvidia-container-toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## 🏭 Production Considerations

### Scalability
- **Inference Workers**: Scale horizontally based on GPU utilization
- **Message Broker**: Partition by camera_id for load distribution
- **Database**: Connection pooling, read replicas for queries
- **Object Storage**: CDN for clip/snapshot delivery

### Security
- JWT tokens with short expiry (15min access, 7d refresh)
- HTTPS only in production
- Encrypted RTSP credentials in database
- Rate limiting on API endpoints
- CORS policy configured per environment
- Audit logs for all sensitive operations

### Monitoring
- Prometheus metrics: inference latency, FPS, queue depth, alerts/sec
- Grafana dashboards for system health
- ELK stack for centralized logging
- Alerting for camera disconnections, high latency, errors

### Data Retention
- Configurable retention policy (30/90/365 days)
- Automated cleanup jobs
- Archive to cold storage (S3 Glacier)

## 🔧 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Inference Workers
```bash
cd inference
docker build -f Dockerfile.gpu -t inference-worker .
docker run --gpus all inference-worker
```

## 📚 API Documentation

- **OpenAPI Spec**: Available at `/docs` (Swagger UI) and `/redoc`
- **Postman Collection**: `docs/postman_collection.json`
- **Architecture Docs**: `docs/architecture.md`

## 🎨 Frontend Components

- **Dashboard**: Multi-camera live grid with online/offline indicators
- **Live Player**: HLS playback with timeline scrubbing
- **Camera View**: Detailed camera view with playback and rules
- **Zone Editor**: Draw polygons/lines for rule zones
- **Alerts**: Real-time alerts feed with filters
- **Rules**: Create and manage detection rules
- **System Health**: Monitor GPU/CPU/Queue lengths

## 🤖 AI Models

### Supported Models
- **Object Detection**: YOLOv8, MobileNet SSD, EfficientDet
- **Face Recognition**: FaceNet, ArcFace
- **License Plate Recognition**: ALPR, Custom OCR
- **Tracking**: DeepSORT, ByteTrack

### Model Conversion
```bash
cd inference
python scripts/convert_pytorch_to_onnx.py --model yolov8n
python scripts/convert_onnx_to_tensorrt.py --model yolov8n
```

### Performance Benchmarks
```bash
cd inference
python benchmarks/run_benchmarks.py
```

## 📊 Performance Targets

- **Throughput**: 30 FPS aggregate across N cameras (GPU dependent)
- **Latency**: <100ms inference per frame
- **Scalability**: Support 50+ cameras per inference worker (GPU)
- **Uptime**: 99.9% availability

## 🛠️ Troubleshooting

### Camera Connection Issues
- Verify RTSP URL with VLC or ffplay
- Check network connectivity and firewall rules
- Ensure camera credentials are correct
- Check camera health endpoint: `GET /api/cameras/{id}/status`

### Inference Performance
- Check GPU utilization: `nvidia-smi`
- Adjust batch size in environment variables
- Monitor queue depth in Prometheus
- Review inference worker logs

### Database Issues
- Check connection pool settings
- Monitor slow queries
- Run migrations: `alembic upgrade head`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- YOLOv8 for object detection
- DeepSORT for object tracking
- FFmpeg for video processing
- FastAPI for the backend framework
- React for the frontend framework

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/DEEPAS-sys/SECUREIN/issues
- Documentation: https://docs.securein.ai
- Email: support@securein.ai

## 🗺️ Roadmap

- [ ] Multi-tenant support
- [ ] Advanced analytics and reporting
- [ ] Mobile app (iOS/Android)
- [ ] Edge deployment support
- [ ] Custom model training pipeline
- [ ] Video search by natural language
- [ ] Integration with VMS platforms
