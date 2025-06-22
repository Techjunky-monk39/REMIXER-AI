# PowerShell script to build, push, and deploy both backend and frontend to Google Cloud Run

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

$project = "remixer-ai"
$region = "us-east1"
$repo = "remixer-repo"

# Backend
$backend_image = "$region-docker.pkg.dev/$project/$repo/flask-app:latest"
$backend_service = "flask-app"

# Frontend
$frontend_image = "$region-docker.pkg.dev/$project/$repo/frontend:latest"
$frontend_service = "frontend"

# Build and push backend
Write-Host "Building backend image..."
docker build -t $backend_image -f flask_app/Dockerfile .
Write-Host "Pushing backend image..."
docker push $backend_image

# Deploy backend to Cloud Run
Write-Host "Deploying backend to Cloud Run..."
gcloud run deploy $backend_service --image=$backend_image --platform=managed --region=$region --allow-unauthenticated

# Get backend URL
$backend_url = gcloud run services describe $backend_service --platform=managed --region=$region --format="value(status.url)"
Write-Host "Backend deployed at: $backend_url"

# Update frontend .env with backend URL
Write-Host "Updating frontend .env with backend URL..."
Set-Content -Path "frontend/.env" -Value "REACT_APP_API_URL=$backend_url"

# Build and push frontend
Write-Host "Building frontend image..."
Set-Location frontend
# Ensure node_modules is not copied into image
if (Test-Path node_modules) { Remove-Item -Recurse -Force node_modules }
docker build -t $frontend_image .
Write-Host "Pushing frontend image..."
docker push $frontend_image
Set-Location ..

# Deploy frontend to Cloud Run
Write-Host "Deploying frontend to Cloud Run..."
gcloud run deploy $frontend_service --image=$frontend_image --platform=managed --region=$region --allow-unauthenticated

# Get frontend URL
$frontend_url = gcloud run services describe $frontend_service --platform=managed --region=$region --format="value(status.url)"
Write-Host "Your frontend is live at: $frontend_url"
Write-Host "You can open this URL on your phone or any device."
