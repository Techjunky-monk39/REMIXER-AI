# REMIXER-AI Production Deployment Script
#
# This script builds and deploys the REMIXER-AI application using Docker Compose (production configuration).
#
# Usage:
#   1. Ensure Docker Desktop is running.
#   2. Run this script in PowerShell: ./deploy.ps1
#
# What it does:
#   - Stops and removes any running containers/images for remixer-python-app and remixer-static-frontend.
#   - Builds fresh Docker images and starts the services using docker-compose.prod.yaml.
#   - Exits with a clear error message if any critical step fails.
#
# For staging or cloud deployment, use deploy-staging.ps1 or deploy-cloudrun.ps1.
#
# Author: [Your Name]
# Date: 2025-06-22
#
# ---
#
# To automate deployment, you can schedule this script to run via Windows Task Scheduler or a CI/CD pipeline.
# Example (Task Scheduler):
#   - Action: Start a program
#   - Program/script: powershell.exe
#   - Add arguments: -ExecutionPolicy Bypass -File "C:\path\to\REMIXER-AI\deploy.ps1"
#
# ---
#
# PowerShell script to clean up and deploy Docker Compose for REMIXER-AI
# Stops and removes containers and images with the same name or image, then builds and runs fresh

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Stop and remove containers with names matching 'remixer-python-app' or 'remixer-static-frontend'
$containers = docker ps -a --filter "name=remixer-python-app" --filter "name=remixer-static-frontend" --format "{{.ID}}"
if ($containers) {
    Write-Host "Stopping and removing containers: $containers"
    try {
        $containers | ForEach-Object { docker stop $_; docker rm $_ }
    } catch {
        Write-Host "ERROR: Failed to stop or remove containers." -ForegroundColor Red
        exit 1
    }
}

# Remove images named 'remixer-python-app' or 'remixer-static-frontend'
$images = docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | Select-String "remixer-python-app|remixer-static-frontend" | ForEach-Object { $_.ToString().Split()[1] }
if ($images) {
    Write-Host "Removing images: $images"
    try {
        $images | ForEach-Object { docker rmi -f $_ }
    } catch {
        Write-Host "ERROR: Failed to remove images." -ForegroundColor Red
        exit 1
    }
}

# Prune unused Docker resources (optional, uncomment if you want a full cleanup)
# docker system prune -f

# Build and deploy with Docker Compose (production)
Write-Host "Building and starting Docker Compose (production)..."
try {
    docker compose -f docker-compose.prod.yaml build --no-cache
    docker compose -f docker-compose.prod.yaml up --remove-orphans
} catch {
    Write-Host "ERROR: Docker Compose build or up failed." -ForegroundColor Red
    exit 1
} # End of last catch block

# End of script
