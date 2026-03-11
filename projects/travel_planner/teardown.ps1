# teardown.ps1 - script to completely delete resources created by deploy.ps1

# Configuration (must match deploy.ps1)
$REGION = "us-central1"
$REPO_NAME = "travel-planner-repo"

Write-Host "🗑️ Starting cleanup of Travel Planner Cloud Run resources..."

Write-Host "🛑 Deleting Cloud Run services..."
gcloud run services delete streamlit-app --region $REGION --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "streamlit-app already deleted or not found." }

gcloud run services delete host-agent --region $REGION --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "host-agent already deleted or not found." }

gcloud run services delete activities-agent --region $REGION --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "activities-agent already deleted or not found." }

gcloud run services delete stay-agent --region $REGION --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "stay-agent already deleted or not found." }

gcloud run services delete flight-agent --region $REGION --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "flight-agent already deleted or not found." }

Write-Host "🛑 Deleting Artifact Registry repository..."
gcloud artifacts repositories delete $REPO_NAME --location=$REGION --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "Repository $REPO_NAME already deleted or not found." }

Write-Host "==============================================="
Write-Host "✅ Cleanup Successful!"
Write-Host "All related Cloud Run services and Docker images have been destroyed."
Write-Host "==============================================="
