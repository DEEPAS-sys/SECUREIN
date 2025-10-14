#!/bin/bash
set -e

echo "Setting up database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing schema"

# Run database migrations
cd backend
python -m alembic upgrade head || echo "No migrations to run"

# Create default admin user
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.db_models import User, UserRole
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == 'admin@example.com'))
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=get_password_hash('admin123'),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            await db.commit()
            print('Admin user created')
        else:
            print('Admin user already exists')

asyncio.run(create_admin())
"

echo "Database setup complete!"
