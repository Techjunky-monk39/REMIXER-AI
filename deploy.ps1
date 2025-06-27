# REMIXER-AI Production Deployment Script
#
# This script builds and deploys the REMIXER-AI application using Docker Compose (production configuration).
#
# Usage:
#   1. Ensure Docker Desktop is running.
#   2. Run this script in PowerShell: ./deploy.ps1
#
# What it does:
#   - Stops and removes any running containers/images for remixer-flask-app and remixer-static-frontend.
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

Write-Host "Stopping and removing all containers for REMIXER-AI..."
docker compose -f docker-compose.prod.yaml down -v --remove-orphans

Write-Host "Removing old images..."
docker rmi remixer-flask-app:latest,remixer-static-frontend:latest -ErrorAction SilentlyContinue

Write-Host "Pruning unused Docker resources..."
docker system prune -af

Write-Host "Building and starting production stack..."
docker compose -f docker-compose.prod.yaml up --build -d

Write-Host "Showing logs (Ctrl+C to exit)..."
docker compose -f docker-compose.prod.yaml logs -f

# End of script
