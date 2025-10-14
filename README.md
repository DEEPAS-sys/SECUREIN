# Video Analytics Platform (Vaidio-like)

A production-ready, end-to-end AI Video Analytics Platform for real-time surveillance and monitoring.

## 🎯 Overview

This platform connects to IP/RTSP cameras, performs real-time AI video analytics (object detection, face recognition, LPR, anomaly detection), applies user-defined rules, generates alerts with stored clips/snapshots, and provides an operator dashboard for live view, alerts, search and configuration.

## 🚀 Quick Start

### Prerequisites

- Docker (20.10+) and Docker Compose (2.0+)
- NVIDIA GPU with CUDA support (for GPU acceleration)
- nvidia-docker runtime (for GPU containers)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/DEEPAS-sys/SECUREIN.git
cd SECUREIN
```

2. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services with Docker Compose**
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
- API Documentation: http://localhost:8000/docs
- MinIO Console: http://localhost:9001
- Grafana: http://localhost:3001

### Default Credentials

- Admin user: `admin@example.com` / `admin123`
- MinIO: `minioadmin` / `minioadmin`
- Grafana: `admin` / `admin`

## 📁 Project Structure

```
/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration and security
│   │   ├── services/    # Business logic services
│   │   ├── models/      # Database and Pydantic models
│   │   ├── db/          # Database configuration
│   │   └── utils/       # Utility modules
│   ├── tests/           # Backend tests
│   └── Dockerfile
├── inference/           # AI inference service
│   ├── models/          # Model storage
│   ├── runners/         # Inference runners
│   └── Dockerfile.gpu
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   └── services/    # API services
│   └── Dockerfile
├── infra/               # Infrastructure as code
│   ├── k8s/             # Kubernetes manifests
│   └── helm/            # Helm charts
├── scripts/             # Utility scripts
├── docs/                # Documentation
└── docker-compose.yml   # Local development setup
```

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI, Python 3.11
- **Database**: PostgreSQL (with SQLAlchemy async)
- **Cache**: Redis
- **Message Broker**: RabbitMQ
- **Search**: Elasticsearch
- **Object Storage**: MinIO (S3-compatible)

### AI/ML
- **Frameworks**: PyTorch, ONNX Runtime, TensorRT
- **Models**: Object Detection (YOLO), Face Recognition, LPR
- **Optimization**: FP16, TensorRT, Batch Processing

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: React Query
- **Real-time**: Socket.io

### Infrastructure
- **Containerization**: Docker, nvidia-docker
- **Orchestration**: Kubernetes, Helm
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack
- **CI/CD**: GitHub Actions

## 🎨 Features

### Camera Management
- Add/remove/configure RTSP/IP cameras
- ONVIF support for camera discovery
- Real-time camera health monitoring
- Multi-camera live view grid

### AI Analytics
- Object detection (person, vehicle, etc.)
- Face recognition with embedding database
- License plate recognition (LPR)
- Object tracking (DeepSort)
- Anomaly detection

### Rules Engine
- Zone-based detection (entry/exit)
- Dwell time monitoring
- Object counting
- Custom rule composition
- Time-based scheduling

### Alerting
- Real-time alert generation
- WebSocket push notifications
- Alert acknowledgment workflow
- Snapshot and video clip storage
- Email/Slack/webhook integrations

### Dashboard
- Live multi-camera view
- Alert feed with filtering
- Video playback and search
- Rule management with visual zone editor
- System health monitoring

### Security
- JWT-based authentication
- Role-based access control (Admin, Operator, Viewer)
- API rate limiting
- Encrypted credentials storage
- Audit logging

## 📊 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

See [docs/openapi.yaml](docs/openapi.yaml) for the full specification.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Smoke Test
```bash
./scripts/run_smoke_test.sh
```

## 🚢 Deployment

### Docker Compose (Development)
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

### Performance Tuning
- GPU batch size: Adjust `INFERENCE_BATCH_SIZE` in `.env`
- Frame sampling rate: Configure per camera (1-30 fps)
- Worker replicas: Scale inference workers based on load
- See [docs/performance.md](docs/performance.md) for details

## 📈 Monitoring

Access monitoring dashboards:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

Key metrics:
- Inference latency and FPS
- Camera connection status
- Alert generation rate
- Queue depths
- GPU utilization

## 🔒 Security Considerations

1. **Credentials**: Use secrets manager in production (AWS Secrets Manager, Vault)
2. **Data Encryption**: RTSP credentials encrypted at rest
3. **Network**: Use VPN/private network for camera access
4. **Data Retention**: Configure per compliance requirements (GDPR, etc.)
5. **Access Control**: Implement SSO/OpenID Connect for enterprise deployment

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Performance Tuning](docs/performance.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- GitHub Issues: https://github.com/DEEPAS-sys/SECUREIN/issues
- Documentation: https://docs.securein.com
- Email: support@securein.com

## ✅ Deliverable Checklist

- [x] Complete repository structure
- [x] Backend FastAPI service with all APIs
- [x] Inference microservices with GPU support
- [x] React frontend with live view and alerts
- [x] Docker Compose for local development
- [x] Kubernetes manifests
- [x] Database migrations (Alembic)
- [x] Unit and integration tests
- [x] OpenAPI documentation
- [x] Camera simulator for testing
- [x] CI/CD pipeline (GitHub Actions)
- [x] Monitoring setup (Prometheus/Grafana)
- [x] Security (JWT, RBAC, rate limiting)
- [x] README and comprehensive documentation
