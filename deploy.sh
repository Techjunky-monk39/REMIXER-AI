#!/bin/bash
# Bash script to clean up and deploy Docker Compose for REMIXER-AI
# Stops and removes containers and images with the same name or image, then builds and runs fresh

set -e

# Stop and remove containers with names matching 'remixer-python-app' or 'remixer-static-frontend'
containers=$(docker ps -a --filter "name=remixer-python-app" --filter "name=remixer-static-frontend" --format "{{.ID}}")
if [ ! -z "$containers" ]; then
    echo "Stopping and removing containers: $containers"
    for c in $containers; do
        docker stop $c
        docker rm $c
    done
fi

# Remove images named 'remixer-python-app' or 'remixer-static-frontend'
images=$(docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep -E 'remixer-python-app|remixer-static-frontend' | awk '{print $2}')
if [ ! -z "$images" ]; then
    echo "Removing images: $images"
    for i in $images; do
        docker rmi -f $i
    done
fi

# Prune unused Docker resources (optional, uncomment if you want a full cleanup)
# docker system prune -f

# Build and deploy with Docker Compose (production)
echo "Building and starting Docker Compose (production)..."
docker compose -f docker-compose.prod.yaml build --no-cache
docker compose -f docker-compose.prod.yaml up --remove-orphans
