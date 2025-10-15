#!/bin/bash

# Load demo data script

set -e

echo "Loading demo data..."

python3 << END
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.db_models import Camera, Rule, RuleType, CameraStatus
from app.core.config import settings
from datetime import datetime

async def load_demo_data():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)
    
    async with AsyncSessionLocal() as session:
        # Create demo cameras
        cameras = [
            Camera(
                name="Front Entrance",
                rtsp_url="rtsp://demo:demo@camera1.example.com/stream1",
                site="Main Office",
                fps=25,
                resolution="1920x1080",
                status=CameraStatus.OFFLINE
            ),
            Camera(
                name="Parking Lot",
                rtsp_url="rtsp://demo:demo@camera2.example.com/stream1",
                site="Main Office",
                fps=25,
                resolution="1920x1080",
                status=CameraStatus.OFFLINE
            ),
            Camera(
                name="Loading Dock",
                rtsp_url="rtsp://demo:demo@camera3.example.com/stream1",
                site="Warehouse",
                fps=25,
                resolution="1920x1080",
                status=CameraStatus.OFFLINE
            )
        ]
        
        session.add_all(cameras)
        await session.flush()
        
        # Create demo rules
        rules = [
            Rule(
                camera_id=cameras[0].id,
                name="Entrance Zone Detection",
                rule_type=RuleType.ZONE_ENTRY,
                enabled=True,
                config={
                    "zone": [[100, 100], [500, 100], [500, 400], [100, 400]],
                    "object_types": ["person"],
                    "threshold": 0.7
                }
            ),
            Rule(
                camera_id=cameras[1].id,
                name="Vehicle Count",
                rule_type=RuleType.OBJECT_COUNT,
                enabled=True,
                config={
                    "zone": [[0, 0], [1920, 0], [1920, 1080], [0, 1080]],
                    "object_types": ["car", "truck"],
                    "count_threshold": 10,
                    "threshold": 0.6
                }
            ),
            Rule(
                camera_id=cameras[2].id,
                name="Dwell Time Alert",
                rule_type=RuleType.DWELL_TIME,
                enabled=True,
                config={
                    "zone": [[200, 200], [600, 200], [600, 600], [200, 600]],
                    "object_types": ["person", "vehicle"],
                    "dwell_time_seconds": 30,
                    "threshold": 0.7
                }
            )
        ]
        
        session.add_all(rules)
        await session.commit()
        
        print(f"Created {len(cameras)} demo cameras")
        print(f"Created {len(rules)} demo rules")
    
    await engine.dispose()

asyncio.run(load_demo_data())
END

echo "Demo data loaded successfully!"
