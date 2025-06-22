# PowerShell script to delete all Cloud Run services in a region for the current project

$region = "us-east1"

# List all Cloud Run services in the region
$services = gcloud run services list --platform=managed --region=$region --format="value(metadata.name)"

if (-not $services) {
    Write-Host "No Cloud Run services found in region ${region}."
    exit 0
}

Write-Host "Deleting the following Cloud Run services in region ${region}:"
$services | ForEach-Object { Write-Host $_ }

$services | ForEach-Object {
    gcloud run services delete $_ --platform=managed --region=$region --quiet
}

Write-Host "All Cloud Run services deleted in region ${region}."
