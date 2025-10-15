#!/bin/bash

# Setup database script

set -e

echo "Setting up database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "${DATABASE_HOST:-localhost}" -U "${DATABASE_USER:-videoadmin}" -d "${DATABASE_NAME:-videodb}" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - running migrations"

# Run Alembic migrations
cd /app/backend
alembic upgrade head

echo "Creating default admin user..."

# Create default admin user
python3 << END
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.db_models import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)
    
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        
        session.add(admin)
        await session.commit()
        print("Admin user created: admin / admin123")
    
    await engine.dispose()

asyncio.run(create_admin())
END

echo "Database setup complete!"
