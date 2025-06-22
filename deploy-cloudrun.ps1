# PowerShell script to build, push, and deploy both backend and frontend to Google Cloud Run

# Ensure all changes are committed and pushed before deployment
git add .
if (-not [string]::IsNullOrWhiteSpace((git status --porcelain))) {
    git commit -m "chore: auto-commit before deploy"
    git push
} else {
    Write-Host "No changes to commit."
}

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

# Health checks for backend and frontend
Write-Host "\nPerforming health checks..."

# Check backend health
try {
    $backend_health = Invoke-WebRequest "$backend_url/healthz" -UseBasicParsing -TimeoutSec 10
    if ($backend_health.StatusCode -eq 200) {
        Write-Host "Backend health check: OK" -ForegroundColor Green
    } else {
        Write-Host "Backend health check: FAILED (status $($backend_health.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Backend health check: FAILED (exception)" -ForegroundColor Red
    exit 1
}

# Check frontend
try {
    $frontend_status = Invoke-WebRequest "$frontend_url" -UseBasicParsing -TimeoutSec 10
    if ($frontend_status.StatusCode -eq 200) {
        Write-Host "Frontend check: OK" -ForegroundColor Green
    } else {
        Write-Host "Frontend check: FAILED (status $($frontend_status.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Frontend check: FAILED (exception)" -ForegroundColor Red
    exit 1
}
