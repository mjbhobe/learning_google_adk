#!/usr/bin/env bash
# deploy.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
REPO_NAME="travel-planner-repo"
IMAGE_NAME="travel-planner"
IMAGE_TAG="latest"
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🚀 Deploying Travel Planner to Cloud Run in project: $PROJECT_ID"
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY is not set. Please export it first:"
    echo "export OPENAI_API_KEY='your-key'"
    exit 1
fi

echo "🔧 Enabling required Google Cloud services..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

echo "📦 Creating Artifact Registry repository (if it doesn't exist)..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION >/dev/null 2>&1; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for Travel Planner"
fi

echo "🏗️ Building and pushing Docker image..."
gcloud builds submit --tag $IMAGE_URL .

echo "☁️ Deploying Flight Agent..."
gcloud run deploy flight-agent \
    --image $IMAGE_URL \
    --region $REGION \
    --set-env-vars="SERVICE_TYPE=flight,OPENAI_API_KEY=$OPENAI_API_KEY" \
    --allow-unauthenticated \
    --format 'value(status.url)' > flight_url.txt
FLIGHT_URL=$(cat flight_url.txt)/run

echo "☁️ Deploying Stay Agent..."
gcloud run deploy stay-agent \
    --image $IMAGE_URL \
    --region $REGION \
    --set-env-vars="SERVICE_TYPE=stay,OPENAI_API_KEY=$OPENAI_API_KEY" \
    --allow-unauthenticated \
    --format 'value(status.url)' > stay_url.txt
STAY_URL=$(cat stay_url.txt)/run

echo "☁️ Deploying Activities Agent..."
gcloud run deploy activities-agent \
    --image $IMAGE_URL \
    --region $REGION \
    --set-env-vars="SERVICE_TYPE=activities,OPENAI_API_KEY=$OPENAI_API_KEY" \
    --allow-unauthenticated \
    --format 'value(status.url)' > activities_url.txt
ACTIVITIES_URL=$(cat activities_url.txt)/run

echo "☁️ Deploying Host Agent..."
gcloud run deploy host-agent \
    --image $IMAGE_URL \
    --region $REGION \
    --set-env-vars="SERVICE_TYPE=host,OPENAI_API_KEY=$OPENAI_API_KEY,FLIGHT_URL=$FLIGHT_URL,STAY_URL=$STAY_URL,ACTIVITIES_URL=$ACTIVITIES_URL" \
    --allow-unauthenticated \
    --format 'value(status.url)' > host_url.txt
HOST_AGENT_URL=$(cat host_url.txt)/run

echo "☁️ Deploying Streamlit App..."
gcloud run deploy streamlit-app \
    --image $IMAGE_URL \
    --region $REGION \
    --set-env-vars="SERVICE_TYPE=streamlit,OPENAI_API_KEY=$OPENAI_API_KEY,HOST_AGENT_URL=$HOST_AGENT_URL" \
    --allow-unauthenticated \
    --format 'value(status.url)' > ui_url.txt
UI_URL=$(cat ui_url.txt)

rm -f flight_url.txt stay_url.txt activities_url.txt host_url.txt ui_url.txt

echo "==============================================="
echo "✅ Deployment Successful!"
echo "You can access your Travel Planner App AT: $UI_URL"
echo "==============================================="
