#!/bin/bash

# Deployment script for BharatGen OpenAI-Compatible API
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e  # Exit on error

ENVIRONMENT=${1:-production}
echo "Deploying to $ENVIRONMENT environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$BHARATGEN_API_KEYS" ] || [ "$BHARATGEN_API_KEYS" = "sk-test-key" ]; then
    echo "Warning: Using default API key! Please set a secure BHARATGEN_API_KEYS in .env"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Pull latest changes (if using git)
if [ -d .git ]; then
    echo "Pulling latest changes..."
    git pull
fi

# Build the Docker image
echo "Building Docker image..."
docker-compose build --no-cache

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Start new containers
echo "Starting containers..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

# Wait for containers to be healthy
echo "Waiting for containers to be healthy..."
sleep 10

# Check if the API is responding
echo "Testing API health..."
HEALTH_RESPONSE=$(curl -s http://localhost:${BHARATGEN_PORT:-8000}/health)
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "✅ Deployment successful!"
    echo "API is running on port ${BHARATGEN_PORT:-8000}"
else
    echo "❌ Health check failed!"
    echo "Response: $HEALTH_RESPONSE"
    docker-compose logs --tail=50
    exit 1
fi

# Show container status
echo ""
echo "Container status:"
docker-compose ps

echo ""
echo "To view logs, run:"
echo "  docker-compose logs -f"

echo ""
echo "To test the API, run:"
echo "  curl http://localhost:${BHARATGEN_PORT:-8000}/health"
