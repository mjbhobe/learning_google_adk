# deploy.ps1
$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_ID = gcloud config get-value project
$REGION = "us-central1"
$REPO_NAME = "travel-planner-repo"
$IMAGE_NAME = "travel-planner"
$IMAGE_TAG = "latest"
$IMAGE_URL = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME`:$IMAGE_TAG"

Write-Host "🚀 Deploying Travel Planner to Cloud Run in project: $PROJECT_ID"
if (-not $env:OPENAI_API_KEY) {
    Write-Host "ERROR: OPENAI_API_KEY is not set. Please set it first:"
    Write-Host "`$env:OPENAI_API_KEY='your-key'"
    exit 1
}

Write-Host "🔧 Enabling required Google Cloud services..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

Write-Host "📦 Creating Artifact Registry repository (if it doesn't exist)..."
$repoExists = gcloud artifacts repositories describe $REPO_NAME --location=$REGION 2>&1
if ($LASTEXITCODE -ne 0) {
    gcloud artifacts repositories create $REPO_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="Docker repository for Travel Planner"
}

Write-Host "🏗️ Building and pushing Docker image..."
gcloud builds submit --tag $IMAGE_URL .

Write-Host "☁️ Deploying Flight Agent..."
$flightUrlRaw = gcloud run deploy flight-agent `
    --image $IMAGE_URL `
    --region $REGION `
    --set-env-vars="SERVICE_TYPE=flight,OPENAI_API_KEY=$env:OPENAI_API_KEY" `
    --allow-unauthenticated `
    --format 'value(status.url)'
$FLIGHT_URL = "$flightUrlRaw/run"

Write-Host "☁️ Deploying Stay Agent..."
$stayUrlRaw = gcloud run deploy stay-agent `
    --image $IMAGE_URL `
    --region $REGION `
    --set-env-vars="SERVICE_TYPE=stay,OPENAI_API_KEY=$env:OPENAI_API_KEY" `
    --allow-unauthenticated `
    --format 'value(status.url)'
$STAY_URL = "$stayUrlRaw/run"

Write-Host "☁️ Deploying Activities Agent..."
$activitiesUrlRaw = gcloud run deploy activities-agent `
    --image $IMAGE_URL `
    --region $REGION `
    --set-env-vars="SERVICE_TYPE=activities,OPENAI_API_KEY=$env:OPENAI_API_KEY" `
    --allow-unauthenticated `
    --format 'value(status.url)'
$ACTIVITIES_URL = "$activitiesUrlRaw/run"

Write-Host "☁️ Deploying Host Agent..."
$hostUrlRaw = gcloud run deploy host-agent `
    --image $IMAGE_URL `
    --region $REGION `
    --set-env-vars="SERVICE_TYPE=host,OPENAI_API_KEY=$env:OPENAI_API_KEY,FLIGHT_URL=$FLIGHT_URL,STAY_URL=$STAY_URL,ACTIVITIES_URL=$ACTIVITIES_URL" `
    --allow-unauthenticated `
    --format 'value(status.url)'
$HOST_AGENT_URL = "$hostUrlRaw/run"

Write-Host "☁️ Deploying Streamlit App..."
$UI_URL = gcloud run deploy streamlit-app `
    --image $IMAGE_URL `
    --region $REGION `
    --set-env-vars="SERVICE_TYPE=streamlit,OPENAI_API_KEY=$env:OPENAI_API_KEY,HOST_AGENT_URL=$HOST_AGENT_URL" `
    --allow-unauthenticated `
    --format 'value(status.url)'

Write-Host "==============================================="
Write-Host "✅ Deployment Successful!"
Write-Host "You can access your Travel Planner App AT: $UI_URL"
Write-Host "==============================================="
