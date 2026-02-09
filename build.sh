#!/bin/bash

# Build script for BharatGen OpenAI-Compatible API
# Usage: ./build.sh [options]
# Options:
#   --no-cache    Build without using cache
#   --tag TAG     Custom tag for the image (default: latest)

set -e  # Exit on error

# Default values
NO_CACHE=""
TAG="latest"
IMAGE_NAME="bharatgen-openai-compatible-api"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./build.sh [--no-cache] [--tag TAG]"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Building BharatGen OpenAI-Compatible API"
echo "=========================================="
echo "Image: $IMAGE_NAME:$TAG"
echo "Cache: $([ -z "$NO_CACHE" ] && echo "enabled" || echo "disabled")"
echo ""

# Check if Dockerfile exists
if [ ! -f Dockerfile ]; then
    echo "Error: Dockerfile not found!"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build $NO_CACHE -t $IMAGE_NAME:$TAG .

# Tag as latest if building with a custom tag
if [ "$TAG" != "latest" ]; then
    echo "Tagging as latest..."
    docker tag $IMAGE_NAME:$TAG $IMAGE_NAME:latest
fi

echo ""
echo "✅ Build complete!"
echo ""
echo "Image details:"
docker images | grep $IMAGE_NAME

echo ""
echo "To run the image:"
echo "  docker run -p 8000:8000 -e BHARATGEN_API_KEYS=sk-test-key $IMAGE_NAME:$TAG"
echo ""
echo "To run with docker-compose:"
echo "  docker-compose up -d"
echo ""
echo "To push to a registry:"
echo "  docker tag $IMAGE_NAME:$TAG your-registry/$IMAGE_NAME:$TAG"
echo "  docker push your-registry/$IMAGE_NAME:$TAG"
