# Deployment Guide

## Local Development

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA GPU with CUDA support (optional, for GPU acceleration)
- nvidia-docker runtime (for GPU containers)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/DEEPAS-sys/SECUREIN.git
cd SECUREIN
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
chmod +x scripts/setup_db.sh
./scripts/setup_db.sh
```

5. **Load demo data (optional)**
```bash
chmod +x scripts/load_demo_data.sh
./scripts/load_demo_data.sh
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### Troubleshooting

**GPU not available:**
If you don't have a GPU, edit `docker-compose.yml` and comment out the GPU-related sections in the `inference` service.

**Port conflicts:**
If ports are already in use, update the port mappings in `docker-compose.yml`.

## Production Deployment (Kubernetes)

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- NVIDIA GPU Operator installed (for GPU nodes)
- Helm 3.x (optional)

### Steps

1. **Create namespace**
```bash
kubectl create namespace video-analytics
```

2. **Create secrets**
```bash
kubectl create secret generic db-credentials \
  --from-literal=postgres-password=your-password \
  -n video-analytics

kubectl create secret generic jwt-secret \
  --from-literal=secret-key=your-jwt-secret \
  -n video-analytics
```

3. **Deploy infrastructure**
```bash
# PostgreSQL
kubectl apply -f infra/k8s/postgres.yaml

# Redis
kubectl apply -f infra/k8s/redis.yaml

# RabbitMQ
kubectl apply -f infra/k8s/rabbitmq.yaml

# MinIO
kubectl apply -f infra/k8s/minio.yaml

# Elasticsearch
kubectl apply -f infra/k8s/elasticsearch.yaml
```

4. **Deploy application**
```bash
kubectl apply -f infra/k8s/deployment.yaml
```

5. **Verify deployment**
```bash
kubectl get pods -n video-analytics
kubectl get services -n video-analytics
```

### Using Helm

```bash
cd infra/helm
helm install video-analytics ./video-analytics \
  --namespace video-analytics \
  --create-namespace \
  --set database.password=your-password \
  --set jwt.secretKey=your-jwt-secret
```

## Cloud Deployment

### AWS

1. **EKS Cluster**
```bash
eksctl create cluster --name video-analytics \
  --region us-east-1 \
  --nodegroup-name gpu-nodes \
  --node-type p3.2xlarge \
  --nodes 2
```

2. **Install NVIDIA Device Plugin**
```bash
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
```

3. **Configure S3 for object storage**
Update `.env` or ConfigMap:
```
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=video-analytics-prod
```

4. **Deploy application**
```bash
kubectl apply -f infra/k8s/
```

### GCP

1. **GKE Cluster with GPU**
```bash
gcloud container clusters create video-analytics \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --machine-type n1-standard-4 \
  --num-nodes 2 \
  --region us-central1
```

2. **Install NVIDIA drivers**
```bash
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

3. **Deploy application**
```bash
kubectl apply -f infra/k8s/
```

### Azure

1. **AKS Cluster**
```bash
az aks create \
  --resource-group video-analytics-rg \
  --name video-analytics-aks \
  --node-count 2 \
  --node-vm-size Standard_NC6 \
  --enable-node-public-ip
```

2. **Install NVIDIA Device Plugin**
```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
```

## Scaling

### Horizontal Pod Autoscaler

```bash
kubectl autoscale deployment inference \
  --cpu-percent=70 \
  --min=1 \
  --max=10 \
  -n video-analytics
```

### Custom Metrics (Queue Depth)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: External
    external:
      metric:
        name: rabbitmq_queue_messages_ready
        selector:
          matchLabels:
            queue: frames
      target:
        type: AverageValue
        averageValue: "100"
```

## Monitoring

### Prometheus + Grafana

```bash
# Install Prometheus Operator
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Deploy monitoring stack
kubectl apply -f infra/k8s/monitoring.yaml
```

### Access Dashboards

```bash
# Port-forward Grafana
kubectl port-forward -n video-analytics svc/grafana 3001:3000

# Open browser
open http://localhost:3001
```

## Backup and Restore

### Database Backup

```bash
# Backup
kubectl exec -n video-analytics postgres-0 -- \
  pg_dump -U postgres video_analytics > backup.sql

# Restore
kubectl exec -i -n video-analytics postgres-0 -- \
  psql -U postgres video_analytics < backup.sql
```

### Object Storage Backup

Configure S3/MinIO lifecycle policies or use cloud-native backup solutions.

## Security Hardening

1. **Enable TLS/SSL**
   - Use cert-manager for automatic certificate management
   - Configure ingress with TLS termination

2. **Network Policies**
```bash
kubectl apply -f infra/k8s/network-policies.yaml
```

3. **Pod Security Policies**
```bash
kubectl apply -f infra/k8s/pod-security-policies.yaml
```

4. **Secrets Management**
   - Use external secrets operator
   - Integrate with AWS Secrets Manager / GCP Secret Manager / Azure Key Vault

## Performance Tuning

See [performance.md](performance.md) for detailed tuning guidelines.
