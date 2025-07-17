#!/bin/bash

echo "🔄 Forcing complete Docker rebuild without cache..."

# Stop all containers
echo "Stopping all containers..."
docker compose down -v

# Remove all images related to this project
echo "Removing project images..."
docker rmi -f $(docker images | grep synapse-lite | awk '{print $3}') 2>/dev/null || echo "No images to remove"

# Prune Docker system
echo "Pruning Docker system..."
docker system prune -af

# Build with no cache
echo "Building with --no-cache flag..."
docker compose build --no-cache

# Start services
echo "Starting services..."
docker compose up -d

echo "✅ Complete rebuild finished!"
echo "Check the logs with: docker compose logs flask-llm-service"