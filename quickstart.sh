#!/bin/bash
# Quick start script for Video Analytics Platform

set -e

echo "=================================="
echo "Video Analytics Platform Quickstart"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "Error: Docker is not installed"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Error: Docker Compose is not installed"; exit 1; }

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "  → Edit .env file to customize configuration"
else
    echo "✓ .env file exists"
fi
echo ""

# Start services
echo "Starting services with Docker Compose..."
echo "This may take a few minutes on first run..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "=================================="
echo "Services Started Successfully! 🎉"
echo "=================================="
echo ""
echo "Access the platform:"
echo "  • Frontend:     http://localhost:3000"
echo "  • Backend API:  http://localhost:8000/docs"
echo "  • MinIO:        http://localhost:9001"
echo "  • Grafana:      http://localhost:3001"
echo "  • Prometheus:   http://localhost:9090"
echo ""
echo "Default credentials:"
echo "  • Admin user:   admin@example.com / admin123"
echo "  • MinIO:        minioadmin / minioadmin"
echo "  • Grafana:      admin / admin"
echo ""
echo "Next steps:"
echo "  1. Initialize database:"
echo "     ./scripts/setup_db.sh"
echo ""
echo "  2. Load demo data (optional):"
echo "     ./scripts/load_demo_data.sh"
echo ""
echo "  3. Login to frontend at http://localhost:3000"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "For help, see:"
echo "  • README.md"
echo "  • docs/troubleshooting.md"
echo "=================================="
