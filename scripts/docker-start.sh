#!/usr/bin/env bash
# Quick start script for QFZZ Docker deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "QFZZ Docker Deployment"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    echo "Install from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p qfzz_audio_content honeycomb logs

# Create placeholder files for volumes
touch qfzz_ledger.json qfzz_knowledge_graph.json

# Ask which services to start
echo ""
echo "Which services do you want to start?"
echo "1) Core services (Icecast + QFZZ + Database)"
echo "2) Core + Frontend"
echo "3) Core + Monitoring"
echo "4) All services"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        COMPOSE_PROFILES=""
        ;;
    2)
        COMPOSE_PROFILES="--profile frontend"
        ;;
    3)
        COMPOSE_PROFILES="--profile monitoring"
        ;;
    4)
        COMPOSE_PROFILES="--profile frontend --profile monitoring"
        ;;
    *)
        echo "Invalid choice, starting core services only"
        COMPOSE_PROFILES=""
        ;;
esac

# Build and start services
echo ""
echo "Building Docker images..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d $COMPOSE_PROFILES

echo ""
echo "========================================"
echo "QFZZ is starting up..."
echo "========================================"
echo ""
echo "Services:"
echo "  - Icecast:  http://localhost:8000"
echo "  - API:      http://localhost:8001"
echo "  - Stream:   http://localhost:8000/qfzz"
echo ""

if [[ $choice == 2 || $choice == 4 ]]; then
    echo "  - Frontend: http://localhost:3001"
fi

if [[ $choice == 3 || $choice == 4 ]]; then
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana:    http://localhost:3002 (admin/admin)"
fi

echo ""
echo "Checking service health..."
sleep 5
docker compose ps

echo ""
echo "View logs with: docker compose logs -f"
echo "Stop services with: docker compose down"
echo ""
