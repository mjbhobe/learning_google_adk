#!/usr/bin/env bash
# teardown.sh - script to completely delete resources created by deploy.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration (must match deploy.sh)
REGION="us-central1"
REPO_NAME="travel-planner-repo"

echo "🗑️ Starting cleanup of Travel Planner Cloud Run resources..."

echo "🛑 Deleting Cloud Run services..."
gcloud run services delete streamlit-app --region $REGION --quiet || echo "streamlit-app already deleted or not found."
gcloud run services delete host-agent --region $REGION --quiet || echo "host-agent already deleted or not found."
gcloud run services delete activities-agent --region $REGION --quiet || echo "activities-agent already deleted or not found."
gcloud run services delete stay-agent --region $REGION --quiet || echo "stay-agent already deleted or not found."
gcloud run services delete flight-agent --region $REGION --quiet || echo "flight-agent already deleted or not found."

echo "🛑 Deleting Artifact Registry repository..."
gcloud artifacts repositories delete $REPO_NAME --location=$REGION --quiet || echo "Repository $REPO_NAME already deleted or not found."

echo "==============================================="
echo "✅ Cleanup Successful!"
echo "All related Cloud Run services and Docker images have been destroyed."
echo "==============================================="
