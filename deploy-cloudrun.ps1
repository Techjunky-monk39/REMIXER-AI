# REMIXER-AI Unified Cloud Run Deployment Script
#
# Usage:
#   ./deploy-cloudrun.ps1 -Environment production
#   ./deploy-cloudrun.ps1 -Environment staging
#
param(
    [ValidateSet("production", "staging")]
    [string]$Environment = "production"
)

# Set variables based on environment
if ($Environment -eq "staging") {
    $TAG = "staging"
    $SERVICE_SUFFIX = "-staging"
    $PROJECT = "remixer-ai-staging"  # Change if your staging project is different
} else {
    $TAG = "latest"
    $SERVICE_SUFFIX = ""
    $PROJECT = "remixer-ai"
}
$REGION = "us-central1"
$REPO = "remixer-repo"

# Check Docker
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check gcloud
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "ERROR: Google Cloud SDK (gcloud) is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Commit and push changes
Write-Host "Checking for uncommitted changes..."
git add .
if (-not [string]::IsNullOrWhiteSpace((git status --porcelain))) {
    try {
        git commit -m "chore: auto-commit before $Environment deploy"
        git push
    } catch {
        Write-Host "ERROR: Git commit or push failed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No changes to commit."
}

# Build and push backend
Write-Host "Building backend Docker image..."
docker build -t $REGION-docker.pkg.dev/$PROJECT/$REPO/flask-app:$TAG -f flask_app/Dockerfile .
Write-Host "Pushing backend Docker image..."
docker push $REGION-docker.pkg.dev/$PROJECT/$REPO/flask-app:$TAG

# Deploy backend to Cloud Run
Write-Host "Deploying backend to Cloud Run..."
gcloud run deploy flask-app$SERVICE_SUFFIX `
    --image=$REGION-docker.pkg.dev/$PROJECT/$REPO/flask-app:$TAG `
    --platform=managed `
    --region=$REGION `
    --allow-unauthenticated `
    --port=8080 `
    --max-instances=1 `
    --timeout=900 `
    --memory=1Gi `
    --cpu=1 `
    --set-env-vars=PYTHONUNBUFFERED=1 `
    --update-env-vars=GUNICORN_CMD_ARGS=--timeout=120 `
    --ingress=all `
    --min-instances=0 `
    --no-cpu-throttling

# Get backend URL
$backendUrl = (gcloud run services describe flask-app$SERVICE_SUFFIX --region $REGION --format="value(status.url)")
if (-not $backendUrl) {
    Write-Host "ERROR: Could not retrieve backend URL." -ForegroundColor Red
    exit 1
}
Write-Host "Backend URL: $backendUrl"

# Update frontend .env
Write-Host "Updating frontend .env with backend URL..."
Set-Content -Path "./frontend/.env" -Value "REACT_APP_BACKEND_URL=$backendUrl"

# Build and push frontend
Write-Host "Building frontend Docker image..."
docker build -t $REGION-docker.pkg.dev/$PROJECT/$REPO/frontend:$TAG -f frontend/Dockerfile ./frontend
Write-Host "Pushing frontend Docker image..."
docker push $REGION-docker.pkg.dev/$PROJECT/$REPO/frontend:$TAG

# Deploy frontend to Cloud Run
Write-Host "Deploying frontend to Cloud Run..."
gcloud run deploy frontend$SERVICE_SUFFIX `
    --image=$REGION-docker.pkg.dev/$PROJECT/$REPO/frontend:$TAG `
    --platform=managed `
    --region=$REGION `
    --allow-unauthenticated `
    --port=8080 `
    --max-instances=1 `
    --timeout=900 `
    --memory=512Mi `
    --cpu=1 `
    --ingress=all `
    --min-instances=0 `
    --no-cpu-throttling

Write-Host "Deployment to $Environment complete!"
