# PowerShell script to build, push, and deploy both backend and frontend to Google Cloud Run (Staging)

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if gcloud CLI is available
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "ERROR: Google Cloud SDK (gcloud) is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Ensure all changes are committed and pushed before deployment
git add .
if (-not [string]::IsNullOrWhiteSpace((git status --porcelain))) {
    try {
        git commit -m "chore: auto-commit before staging deploy"
        git push
    } catch {
        Write-Host "ERROR: Git commit or push failed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No changes to commit."
}

$project = "remixer-ai-staging"  # Use your staging project name
$region = "us-east1"
$repo = "remixer-repo"

# Backend
$backend_image = "$region-docker.pkg.dev/$project/$repo/flask-app:staging"
$backend_service = "flask-app-staging"

# Frontend
$frontend_image = "$region-docker.pkg.dev/$project/$repo/frontend:staging"
$frontend_service = "frontend-staging"

# Build and push backend
Write-Host "Building backend image..."
try {
    docker build -t $backend_image -f flask_app/Dockerfile .
    docker push $backend_image
} catch {
    Write-Host "ERROR: Failed to build or push backend image." -ForegroundColor Red
    exit 1
}

# Deploy backend to Cloud Run
Write-Host "Deploying backend to Cloud Run (staging)..."
try {
    gcloud run deploy $backend_service --image=$backend_image --platform=managed --region=$region --allow-unauthenticated
} catch {
    Write-Host "ERROR: Failed to deploy backend to Cloud Run (staging)." -ForegroundColor Red
    exit 1
}

# Get backend URL
$backend_url = gcloud run services describe $backend_service --platform=managed --region=$region --format="value(status.url)"
Write-Host "Backend (staging) deployed at: $backend_url"

# Update frontend .env with backend URL
Write-Host "Updating frontend .env with backend URL (staging)..."
Set-Content -Path "frontend/.env" -Value "REACT_APP_API_URL=$backend_url"

# Build and push frontend
Write-Host "Building frontend image..."
Set-Location frontend
if (Test-Path node_modules) { Remove-Item -Recurse -Force node_modules }
try {
    docker build -t $frontend_image .
    docker push $frontend_image
} catch {
    Write-Host "ERROR: Failed to build or push frontend image." -ForegroundColor Red
    exit 1
}
Set-Location ..

# Deploy frontend to Cloud Run
Write-Host "Deploying frontend to Cloud Run (staging)..."
try {
    gcloud run deploy $frontend_service --image=$frontend_image --platform=managed --region=$region --allow-unauthenticated
} catch {
    Write-Host "ERROR: Failed to deploy frontend to Cloud Run (staging)." -ForegroundColor Red
    exit 1
}

# Get frontend URL
$frontend_url = gcloud run services describe $frontend_service --platform=managed --region=$region --format="value(status.url)"
Write-Host "Your frontend (staging) is live at: $frontend_url"
Write-Host "You can open this URL on your phone or any device."

# Health checks for backend and frontend
Write-Host "\nPerforming health checks (staging)..."

# Check backend health
try {
    $backend_health = Invoke-WebRequest "$backend_url/healthz" -UseBasicParsing -TimeoutSec 10
    if ($backend_health.StatusCode -eq 200) {
        Write-Host "Backend health check (staging): OK" -ForegroundColor Green
    } else {
        Write-Host "Backend health check (staging): FAILED (status $($backend_health.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Backend health check (staging): FAILED (exception)" -ForegroundColor Red
    exit 1
}

# Check frontend
try {
    $frontend_status = Invoke-WebRequest "$frontend_url" -UseBasicParsing -TimeoutSec 10
    if ($frontend_status.StatusCode -eq 200) {
        Write-Host "Frontend check (staging): OK" -ForegroundColor Green
    } else {
        Write-Host "Frontend check (staging): FAILED (status $($frontend_status.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Frontend check (staging): FAILED (exception)" -ForegroundColor Red
    exit 1
}
# End of script
