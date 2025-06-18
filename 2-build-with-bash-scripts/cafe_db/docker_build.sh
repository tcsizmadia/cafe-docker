#!/bin/bash

# Set variables
SERVICE_NAME="cafe-db"
IMAGE_NAME="cafe-docker/${SERVICE_NAME}"
IMAGE_TAG="latest"


echo "Building cafe-db PostgreSQL service image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    echo "✅ Successfully built ${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo "❌ Failed to build ${IMAGE_NAME}:${IMAGE_TAG}"
    exit 1
fi
