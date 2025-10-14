# Performance Tuning Guide

## Inference Optimization

### GPU Configuration

1. **Batch Size**
   - Increase batch size to maximize GPU utilization
   - Trade-off: Higher latency vs. better throughput
   - Recommended: 4-8 for real-time, 16-32 for batch processing

```env
INFERENCE_BATCH_SIZE=8
```

2. **Mixed Precision (FP16)**
   - Enable FP16 for 2-3x speedup on modern GPUs
   - Minimal accuracy loss for most models

```env
INFERENCE_FP16=true
```

3. **TensorRT Optimization**
```bash
# Convert ONNX to TensorRT
trtexec --onnx=model.onnx \
        --saveEngine=model.trt \
        --fp16 \
        --workspace=4096
```

### Model Selection

| Model | Resolution | FPS (GPU) | FPS (CPU) | Accuracy |
|-------|-----------|-----------|-----------|----------|
| YOLOv5s | 640x640 | 120 | 15 | Good |
| YOLOv5m | 640x640 | 80 | 8 | Better |
| YOLOv8n | 640x640 | 150 | 20 | Good |
| Faster R-CNN | 800x800 | 25 | 2 | Best |

### Frame Sampling

- Reduce FPS for analytics (5 fps is usually sufficient)
- Higher FPS only for fast-moving objects

```env
FRAME_SAMPLING_FPS=5
```

## Database Optimization

### Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_camera_id ON alerts(camera_id);
CREATE INDEX idx_detections_alert_id ON detections(alert_id);
CREATE INDEX idx_cameras_status ON cameras(status);
```

### Connection Pooling

```env
# PostgreSQL
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=10
```

### Partitioning

Partition alerts table by timestamp for better query performance:

```sql
CREATE TABLE alerts_2024_01 PARTITION OF alerts
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Redis Optimization

### Memory Configuration

```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Pipeline Usage

```python
# Batch Redis operations
pipe = redis.pipeline()
for i in range(1000):
    pipe.set(f'key_{i}', value)
pipe.execute()
```

## Message Queue Optimization

### RabbitMQ

```
# rabbitmq.conf
vm_memory_high_watermark.relative = 0.6
disk_free_limit.absolute = 10GB
```

### Prefetch Count

```python
# Consumer prefetch
channel.basic_qos(prefetch_count=10)
```

## Network Optimization

### RTSP Streaming

- Use TCP for reliability: `-rtsp_transport tcp`
- Reduce resolution if bandwidth limited
- Use H.264 hardware encoding when available

### HLS Configuration

```
# Segment duration
HLS_SEGMENT_DURATION=4

# Playlist size
HLS_LIST_SIZE=10
```

## System Tuning

### Linux Kernel

```bash
# Increase file descriptors
ulimit -n 65535

# Network buffer sizes
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
```

### Docker

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Monitoring Metrics

### Key Performance Indicators

1. **Inference Latency**: Target < 100ms per frame
2. **Frame Processing Rate**: Frames/sec per camera
3. **Queue Depth**: Should stay < 1000
4. **Alert Generation Rate**: Alerts/sec
5. **Database Query Time**: < 50ms for reads
6. **API Response Time**: < 200ms (p95)

### Prometheus Queries

```promql
# Inference latency
histogram_quantile(0.95, rate(inference_duration_seconds_bucket[5m]))

# Queue depth
rabbitmq_queue_messages_ready{queue="frames"}

# API latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Scaling Guidelines

### Vertical Scaling

| Component | CPU | Memory | GPU | Storage |
|-----------|-----|--------|-----|---------|
| Backend | 2-4 | 4-8GB | - | 100GB |
| Inference | 4-8 | 8-16GB | 1xT4 | 50GB |
| Frontend | 1-2 | 2-4GB | - | 10GB |
| PostgreSQL | 4-8 | 16-32GB | - | 500GB SSD |
| Redis | 2-4 | 8-16GB | - | 50GB |

### Horizontal Scaling

1. **Backend API**: 2-4 replicas behind load balancer
2. **Inference Workers**: Scale based on camera count
   - Rule of thumb: 1 GPU worker per 10 cameras at 5fps
3. **Database**: Read replicas for heavy read workloads

### Auto-scaling Formula

```
desired_replicas = ceil(queue_depth / target_queue_per_replica)
```

Where:
- `queue_depth`: Current number of frames in queue
- `target_queue_per_replica`: 100-200 frames

## Cost Optimization

### GPU Instance Selection

| Cloud | Instance Type | GPU | Cost/hour | Cameras* |
|-------|--------------|-----|-----------|----------|
| AWS | g4dn.xlarge | T4 | $0.526 | 8-12 |
| AWS | p3.2xlarge | V100 | $3.06 | 30-40 |
| GCP | n1-standard-4-t4 | T4 | $0.48 | 8-12 |
| Azure | NC6s_v3 | V100 | $3.06 | 30-40 |

*Estimated at 5fps per camera with YOLOv5s

### Spot Instances

Use spot instances for inference workers (interruptible workload):
- AWS EC2 Spot: 70-90% savings
- GCP Preemptible VMs: 80% savings
- Azure Spot VMs: 80% savings

### Storage Optimization

1. **Retention Policies**
   - Keep snapshots: 30 days
   - Keep clips: 7 days
   - Archive to cold storage: > 90 days

2. **Compression**
   - JPEG quality: 75-85
   - Video codec: H.264 with CRF 23-28

## Troubleshooting Performance Issues

### High Latency

1. Check queue depth
2. Verify GPU utilization
3. Profile database queries
4. Check network bandwidth

### Low FPS

1. Reduce batch size
2. Use smaller model
3. Enable FP16
4. Check RTSP connection quality

### Memory Issues

1. Limit batch size
2. Clear Redis cache
3. Implement pagination
4. Use connection pooling

### GPU Utilization Low

1. Increase batch size
2. Add more cameras
3. Use multi-stream inference
4. Check CPU bottleneck
