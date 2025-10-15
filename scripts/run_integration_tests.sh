#!/bin/bash

# Integration tests script

set -e

echo "Running integration tests..."

# Start docker-compose services
echo "Starting services..."
docker-compose up -d postgres redis rabbitmq minio

# Wait for services to be ready
echo "Waiting for services..."
sleep 10

# Run backend tests
echo "Running backend tests..."
cd backend
pytest app/tests/ -v

# Run end-to-end test
echo "Running end-to-end smoke test..."
python3 << END
import asyncio
import httpx

async def smoke_test():
    base_url = "http://localhost:8000"
    
    # Register user
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get(f"{base_url}/health")
        assert response.status_code == 200
        print("✓ Health check passed")
        
        # Register user
        response = await client.post(
            f"{base_url}/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
                "role": "admin"
            }
        )
        assert response.status_code == 201
        print("✓ User registration passed")
        
        # Login
        response = await client.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        print("✓ Login passed")
        
        # Create camera
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            f"{base_url}/api/cameras",
            headers=headers,
            json={
                "name": "Test Camera",
                "rtsp_url": "rtsp://test.example.com/stream",
                "fps": 25,
                "resolution": "1920x1080"
            }
        )
        assert response.status_code == 201
        camera_id = response.json()["id"]
        print(f"✓ Camera creation passed (ID: {camera_id})")
        
        # Create rule
        response = await client.post(
            f"{base_url}/api/rules",
            headers=headers,
            json={
                "camera_id": camera_id,
                "name": "Test Rule",
                "rule_type": "zone_entry",
                "enabled": True,
                "config": {
                    "zone": [[0, 0], [100, 0], [100, 100], [0, 100]],
                    "object_types": ["person"],
                    "threshold": 0.7
                }
            }
        )
        assert response.status_code == 201
        print("✓ Rule creation passed")
        
        print("\n✅ All integration tests passed!")

asyncio.run(smoke_test())
END

echo "Integration tests complete!"
