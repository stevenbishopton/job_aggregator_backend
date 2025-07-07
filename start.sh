#!/bin/bash

# Start Celery worker in background
celery -A app.celery_config.celery_app worker --loglevel=INFO &

# Start dummy web server (required for Cloud Run)
uvicorn app.main:app --host 0.0.0.0 --port $PORT 