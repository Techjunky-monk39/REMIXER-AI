# PowerShell script to clean up and deploy Docker Compose for REMIXER-AI
# Stops and removes containers and images with the same name or image, then builds and runs fresh

# Stop and remove containers with names matching 'remixer-python-app' or 'remixer-static-frontend'
$containers = docker ps -a --filter "name=remixer-python-app" --filter "name=remixer-static-frontend" --format "{{.ID}}"
if ($containers) {
    Write-Host "Stopping and removing containers: $containers"
    $containers | ForEach-Object { docker stop $_; docker rm $_ }
}

# Remove images named 'remixer-python-app' or 'remixer-static-frontend'
$images = docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | Select-String "remixer-python-app|remixer-static-frontend" | ForEach-Object { $_.ToString().Split()[1] }
if ($images) {
    Write-Host "Removing images: $images"
    $images | ForEach-Object { docker rmi -f $_ }
}

# Prune unused Docker resources (optional, uncomment if you want a full cleanup)
# docker system prune -f

# Build and deploy with Docker Compose (production)
Write-Host "Building and starting Docker Compose (production)..."
docker compose -f docker-compose.prod.yaml build --no-cache
docker compose -f docker-compose.prod.yaml up --remove-orphans
