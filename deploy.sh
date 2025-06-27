#!/bin/bash
# Bash script to clean up and deploy Docker Compose for REMIXER-AI
# Stops and removes containers and images with the same name or image, then builds and runs fresh

set -e

echo "Stopping and removing all containers for REMIXER-AI..."
docker compose -f docker-compose.prod.yaml down -v --remove-orphans || true

echo "Removing old images..."
docker rmi remixer-flask-app:latest remixer-static-frontend:latest || true

echo "Pruning unused Docker resources..."
docker system prune -af || true

echo "Building and starting production stack..."
docker compose -f docker-compose.prod.yaml up --build -d

echo "Showing logs (Ctrl+C to exit)..."
docker compose -f docker-compose.prod.yaml logs -f
