#!/bin/bash

# Script to build the POS Service Docker image
# This script demonstrates a simple approach to Docker image building.

# Set variables
SERVICE_NAME="pos-service"
IMAGE_NAME="cafe-docker/${SERVICE_NAME}"
IMAGE_TAG="latest"

# Display build information
echo "Building ${SERVICE_NAME} Docker image..."
echo "Image name: ${IMAGE_NAME}:${IMAGE_TAG}"

# Build the Docker image
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Successfully built ${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo "❌ Failed to build ${IMAGE_NAME}:${IMAGE_TAG}"
    exit 1
fi
