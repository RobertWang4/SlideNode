#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <PROJECT_ID> <REGION> <IMAGE_TAG> <SERVICE_ACCOUNT_EMAIL>"
  exit 1
fi

PROJECT_ID="$1"
REGION="$2"
IMAGE_TAG="$3"
SERVICE_ACCOUNT="$4"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
API_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/slidenode/api:${IMAGE_TAG}"
WORKER_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/slidenode/worker:${IMAGE_TAG}"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/slidenode/frontend:${IMAGE_TAG}"

cd "${ROOT_DIR}"

gcloud config set project "${PROJECT_ID}"

echo "Building and pushing backend image..."
gcloud builds submit backend --tag "${API_IMAGE}"
gcloud builds submit backend --tag "${WORKER_IMAGE}"

echo "Building and pushing frontend image..."
gcloud builds submit frontend --tag "${FRONTEND_IMAGE}"

echo "Deploying API service..."
gcloud run deploy slidenode-api \
  --image "${API_IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "${SERVICE_ACCOUNT}" \
  --env-vars-file infra/gcp/cloudrun.env.example

echo "Deploying Worker service..."
gcloud run deploy slidenode-worker \
  --image "${WORKER_IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account "${SERVICE_ACCOUNT}" \
  --command celery \
  --args "-A,app.workers.celery_app.celery_app,worker,-l,info" \
  --env-vars-file infra/gcp/cloudrun.env.example

echo "Deploying Frontend service..."
gcloud run deploy slidenode-frontend \
  --image "${FRONTEND_IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated

echo "Done. Configure frontend VITE_API_BASE_URL to your API URL if needed."
