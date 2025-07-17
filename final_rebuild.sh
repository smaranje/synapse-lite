#!/bin/bash

echo "🔄 Final rebuild with fresh app.py file..."

# Verify the new app.py is clean
echo "Checking app.py for merge conflicts..."
if grep -q "<<<<<<" ai_service/app.py; then
    echo "❌ ERROR: app.py still contains merge conflicts!"
    exit 1
else
    echo "✅ app.py is clean"
fi

# Stop all containers
echo "Stopping all containers..."
docker compose down -v

# Remove ALL Docker data to ensure clean slate
echo "Removing all Docker images and cache..."
docker system prune -af --volumes

# Remove specific project images if they exist
docker rmi -f $(docker images -q --filter "reference=*synapse-lite*") 2>/dev/null || echo "No project images to remove"

# Force rebuild without any cache
echo "Building with --no-cache and --pull..."
docker compose build --no-cache --pull

# Start services
echo "Starting services..."
docker compose up -d

echo "✅ Final rebuild completed!"
echo ""
echo "Check the Flask service logs:"
echo "docker compose logs flask-llm-service"
echo ""
echo "Test the health endpoint:"
echo "curl http://localhost:5000/health"