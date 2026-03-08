# StageSense — Root Dockerfile
#
# Bug 1 FIX: Dockerfile moved to stagesense/ root so both backend/ and frontend/
# are within the build context. The previous Dockerfile in backend/ used
# "COPY ../frontend" which escapes the build context and fails on Cloud Run.
#
# Bug 10 FIX: Added --proxy-headers and --forwarded-allow-ips to uvicorn CMD.
# Cloud Run terminates TLS — without proxy-headers, wss:// WebSocket handshakes
# fail because uvicorn doesn't trust the X-Forwarded-Proto header.
#
# Deploy from stagesense/ root:
#   gcloud run deploy stagesense --source . --region us-central1 \
#     --allow-unauthenticated --timeout 3600 --memory 1Gi \
#     --set-env-vars GOOGLE_CLOUD_PROJECT=ai-hack-489018,GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=us-central1
#
# NOTE: --workers 1 is required. Multiple workers = multiple processes = global
# latest_scores dict is NOT shared. Single worker ensures SSE always reflects
# the live session's scores.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy frontend into the image (served as static files by FastAPI)
# Bug 1 FIX: This COPY now works because Dockerfile is at stagesense/ root
COPY frontend/ ./frontend/

EXPOSE 8080

# Bug 10 FIX: --proxy-headers trusts X-Forwarded-Proto from Cloud Run's
# TLS proxy, enabling wss:// WebSocket connections to work correctly.
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--workers", "1", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
