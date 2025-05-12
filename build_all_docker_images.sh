#!/bin/bash

# Simple build script for all Docker images in the Cafe Docker project
# This script demonstrates a basic approach to Docker image building.

echo "====== Building all Docker images for Cafe Docker ======"

echo "Building cafe_db service..."
cd cafe_db && ./docker_build.sh
if [ $? -ne 0 ]; then
    echo "Failed to build cafe_db"
    exit 1
fi
cd ..

echo "Building api_gateway service..."
cd api_gateway && ./docker_build.sh
if [ $? -ne 0 ]; then
    echo "Failed to build api_gateway"
    exit 1
fi
cd ..

echo "Building loyalty_service service..."
cd loyalty_service && ./docker_build.sh
if [ $? -ne 0 ]; then
    echo "Failed to build loyalty_service"
    exit 1
fi
cd ..

echo "Building menu_service service..."
cd menu_service && ./docker_build.sh
if [ $? -ne 0 ]; then
    echo "Failed to build menu_service"
    exit 1
fi
cd ..

echo "Building pos_service service..."
cd pos_service && ./docker_build.sh
if [ $? -ne 0 ]; then
    echo "Failed to build pos_service"
    exit 1
fi
cd ..

echo "====== All services built successfully ======"
echo "Use docker-compose-with-images.yml to run services with pre-built images"
