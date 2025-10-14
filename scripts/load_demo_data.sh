#!/bin/bash
set -e

echo "Loading demo data..."

# Create demo cameras
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.db_models import Camera, CameraStatus

async def load_demo_cameras():
    async with AsyncSessionLocal() as db:
        cameras = [
            Camera(
                name='Front Entrance',
                rtsp_url='rtsp://demo:demo@localhost:8554/stream1',
                site='Main Building',
                fps=5,
                resolution='1920x1080',
                enabled=True,
                status=CameraStatus.OFFLINE
            ),
            Camera(
                name='Parking Lot',
                rtsp_url='rtsp://demo:demo@localhost:8554/stream2',
                site='Main Building',
                fps=5,
                resolution='1920x1080',
                enabled=True,
                status=CameraStatus.OFFLINE
            ),
            Camera(
                name='Warehouse',
                rtsp_url='rtsp://demo:demo@localhost:8554/stream3',
                site='Warehouse',
                fps=5,
                resolution='1920x1080',
                enabled=True,
                status=CameraStatus.OFFLINE
            ),
        ]
        
        for camera in cameras:
            db.add(camera)
        
        await db.commit()
        print(f'{len(cameras)} demo cameras created')

asyncio.run(load_demo_cameras())
"

echo "Demo data loaded successfully!"
