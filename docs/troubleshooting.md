# Troubleshooting Guide

## Common Issues

### Docker Compose

#### Services Won't Start

**Problem:** Services fail to start or crash immediately

**Solutions:**
```bash
# Check logs
docker-compose logs [service-name]

# Check for port conflicts
netstat -tulpn | grep [port]

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

#### GPU Not Available

**Problem:** Inference service can't access GPU

**Solutions:**
```bash
# Install nvidia-docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Alternative: Use CPU inference
# Edit docker-compose.yml and comment out GPU-related sections
```

#### Database Connection Issues

**Problem:** Backend can't connect to PostgreSQL

**Solutions:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database credentials
docker-compose exec postgres psql -U postgres -d video_analytics

# Reset database
docker-compose down -v
docker-compose up -d postgres
./scripts/setup_db.sh
```

### Backend

#### Import Errors

**Problem:** Module not found errors

**Solutions:**
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

#### Database Migration Errors

**Problem:** Alembic migration fails

**Solutions:**
```bash
# Initialize alembic (if not done)
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial"

# Apply migration
alembic upgrade head

# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
```

#### Authentication Issues

**Problem:** JWT token errors or unauthorized access

**Solutions:**
```bash
# Check JWT secret is set
echo $JWT_SECRET_KEY

# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Clear browser localStorage
# In browser console:
localStorage.clear()
```

### Frontend

#### Build Errors

**Problem:** npm build fails

**Solutions:**
```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Try building again
npm run build
```

#### API Connection Errors

**Problem:** Frontend can't reach backend

**Solutions:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend
# Edit backend/app/core/config.py
# Verify CORS_ORIGINS includes frontend URL

# Check proxy configuration in vite.config.ts
```

#### WebSocket Connection Issues

**Problem:** Real-time alerts not working

**Solutions:**
```bash
# Check WebSocket endpoint
# In browser console:
const ws = new WebSocket('ws://localhost:8000/ws/alerts')
ws.onopen = () => console.log('Connected')
ws.onerror = (e) => console.error('Error:', e)

# Check Nginx proxy settings if using
# Ensure WebSocket headers are set
```

### Inference

#### Model Loading Errors

**Problem:** Can't load AI models

**Solutions:**
```bash
# Download pretrained models
cd inference/models
# Follow instructions in models/README.md

# Use CPU fallback
# Edit docker-compose.yml
# Set INFERENCE_DEVICE=cpu
```

#### Out of Memory

**Problem:** GPU out of memory errors

**Solutions:**
```bash
# Reduce batch size
# Edit .env
INFERENCE_BATCH_SIZE=2  # Default is 4

# Check GPU memory
nvidia-smi

# Use smaller model
# Edit inference/runners/detect.py
# Use YOLOv5s instead of larger models
```

### Performance

#### Slow API Responses

**Problem:** API endpoints are slow

**Solutions:**
```bash
# Check database connections
# Add indexes
docker-compose exec postgres psql -U postgres -d video_analytics

# Check Redis
docker-compose exec redis redis-cli ping

# Enable query logging
# Edit backend/app/core/config.py
DEBUG=True
```

#### High CPU Usage

**Problem:** Services using too much CPU

**Solutions:**
```bash
# Check Docker stats
docker stats

# Limit resources in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G

# Scale down workers
# Reduce INFERENCE_WORKERS in .env
```

### Kubernetes

#### Pods Not Starting

**Problem:** Pods stuck in pending or crash loop

**Solutions:**
```bash
# Check pod status
kubectl get pods -n video-analytics

# Describe pod
kubectl describe pod [pod-name] -n video-analytics

# Check logs
kubectl logs [pod-name] -n video-analytics

# Check resources
kubectl top nodes
kubectl top pods -n video-analytics
```

#### GPU Nodes Not Available

**Problem:** Inference pods can't schedule on GPU nodes

**Solutions:**
```bash
# Check GPU nodes
kubectl get nodes -l accelerator=nvidia

# Install NVIDIA device plugin
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

# Verify GPU resources
kubectl get nodes -o json | jq '.items[].status.capacity'
```

### Monitoring

#### Metrics Not Appearing

**Problem:** Prometheus not scraping metrics

**Solutions:**
```bash
# Check Prometheus targets
# Visit http://localhost:9090/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus config
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
```

#### Grafana Dashboard Issues

**Problem:** Dashboards not loading data

**Solutions:**
```bash
# Check Prometheus data source
# Grafana UI → Configuration → Data Sources

# Check Prometheus is accessible
docker-compose exec grafana wget -O- http://prometheus:9090/-/healthy
```

## Debugging Tips

### Enable Debug Logging

```bash
# Backend
# Edit .env
LOG_LEVEL=DEBUG

# Check logs
docker-compose logs -f backend
```

### Database Inspection

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d video_analytics

# List tables
\dt

# Query data
SELECT * FROM users;
SELECT * FROM cameras;
SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10;
```

### Network Debugging

```bash
# Check connectivity between services
docker-compose exec backend ping postgres
docker-compose exec backend ping redis

# Check DNS resolution
docker-compose exec backend nslookup postgres
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping

# RabbitMQ
curl http://localhost:15672/api/health/checks/alarms
```

## Getting Help

If you can't resolve an issue:

1. Check existing GitHub issues
2. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Logs and error messages
   - Environment details (OS, Docker version, etc.)
3. Join our community chat (if available)

## Performance Profiling

### Backend Profiling

```python
# Add to backend code
import cProfile
import pstats

def profile_endpoint():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### Database Query Analysis

```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Memory Profiling

```bash
# Python memory profiler
pip install memory-profiler
python -m memory_profiler backend/app/main.py

# Docker memory usage
docker stats --no-stream
```
