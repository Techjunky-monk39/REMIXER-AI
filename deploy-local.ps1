# PowerShell script to clean, build, and deploy all services locally with Docker Compose

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Cleaning up old containers and images..."
try {
    docker compose down --volumes --remove-orphans
    docker system prune -f
} catch {
    Write-Host "ERROR: Docker cleanup failed." -ForegroundColor Red
    exit 1
}

git add .
if (-not [string]::IsNullOrWhiteSpace((git status --porcelain))) {
    try {
        git commit -m "chore: auto-commit before local deploy"
        git push
    } catch {
        Write-Host "ERROR: Git commit or push failed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No changes to commit."
}

Write-Host "Building and starting all services with Docker Compose..."
try {
    docker compose up --build -d
} catch {
    Write-Host "ERROR: Docker Compose up failed." -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 10

# Health checks
$backend_url = "http://localhost:8080/healthz"
$frontend_url = "http://localhost:3001"
$static_url = "http://localhost:3000"

Write-Host "\nPerforming health checks..."

try {
    $backend_health = Invoke-WebRequest $backend_url -UseBasicParsing -TimeoutSec 10
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

try {
    $frontend_status = Invoke-WebRequest $frontend_url -UseBasicParsing -TimeoutSec 10
    if ($frontend_status.StatusCode -eq 200) {
        Write-Host "React frontend check: OK" -ForegroundColor Green
    } else {
        Write-Host "React frontend check: FAILED (status $($frontend_status.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "React frontend check: FAILED (exception)" -ForegroundColor Red
    exit 1
}

try {
    $static_status = Invoke-WebRequest $static_url -UseBasicParsing -TimeoutSec 10
    if ($static_status.StatusCode -eq 200) {
        Write-Host "Static site check: OK" -ForegroundColor Green
    } else {
        Write-Host "Static site check: FAILED (status $($static_status.StatusCode))" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Static site check: FAILED (exception)" -ForegroundColor Red
    exit 1
}

Write-Host "\nAll services are up and healthy!"
Write-Host "Backend:   http://localhost:8080"
Write-Host "Frontend:  http://localhost:3001"
Write-Host "Static:    http://localhost:3000"
# End of script
