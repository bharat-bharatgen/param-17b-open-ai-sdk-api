# Makefile for BharatGen OpenAI-Compatible API

.PHONY: help build build-no-cache run stop test deploy clean push

# Default target
help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker image"
	@echo "  make build-no-cache - Build Docker image without cache"
	@echo "  make run            - Run the container locally"
	@echo "  make stop           - Stop running containers"
	@echo "  make test           - Run endpoint tests"
	@echo "  make deploy         - Deploy to production"
	@echo "  make clean          - Remove containers and images"
	@echo "  make push           - Push image to registry"
	@echo "  make logs           - View container logs"
	@echo ""
	@echo "Environment-specific:"
	@echo "  make run-dev        - Run in development mode"
	@echo "  make run-prod       - Run in production mode (with nginx)"
	@echo "  make run-simple     - Run in simple production mode (no nginx)"

# Build commands
build:
	@echo "Building Docker image..."
	docker build -t bharatgen-openai-compatible-api:latest .

build-no-cache:
	@echo "Building Docker image (no cache)..."
	docker build --no-cache -t bharatgen-openai-compatible-api:latest .

# Run commands
run:
	@echo "Starting development environment..."
	docker-compose up -d

run-dev:
	@echo "Starting development environment..."
	docker-compose up

run-simple:
	@echo "Starting simple production environment..."
	docker-compose -f docker-compose.simple.yml up -d

run-prod:
	@echo "Starting production environment with nginx..."
	docker-compose -f docker-compose.prod.yml up -d

# Stop commands
stop:
	@echo "Stopping containers..."
	docker-compose down

stop-all:
	@echo "Stopping all configurations..."
	docker-compose down
	docker-compose -f docker-compose.simple.yml down
	docker-compose -f docker-compose.prod.yml down

# Testing
test:
	@echo "Running endpoint tests..."
	@if [ -f test_docker_endpoints.sh ]; then \
		./test_docker_endpoints.sh 8000; \
	else \
		echo "Error: test_docker_endpoints.sh not found!"; \
		exit 1; \
	fi

test-local:
	@echo "Testing local Python installation..."
	python -m bharatgen_openai.server &
	@sleep 5
	@./test_docker_endpoints.sh 8000
	@pkill -f "python -m bharatgen_openai.server"

# Deployment
deploy:
	@echo "Deploying to production..."
	@if [ -f deploy.sh ]; then \
		./deploy.sh production; \
	else \
		echo "Error: deploy.sh not found!"; \
		exit 1; \
	fi

# Logs
logs:
	docker-compose logs -f

logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f

# Clean up
clean:
	@echo "Removing containers and images..."
	docker-compose down -v
	docker rmi bharatgen-openai-compatible-api:latest || true

clean-all:
	@echo "Removing all containers, images, and volumes..."
	docker-compose down -v
	docker-compose -f docker-compose.simple.yml down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker rmi bharatgen-openai-compatible-api:latest || true
	docker system prune -f

# Registry operations
push:
	@echo "Pushing to Docker registry..."
	@read -p "Enter registry URL (e.g., docker.io/username): " REGISTRY; \
	docker tag bharatgen-openai-compatible-api:latest $$REGISTRY/bharatgen-openai-compatible-api:latest; \
	docker push $$REGISTRY/bharatgen-openai-compatible-api:latest

# Development helpers
shell:
	docker-compose exec bharatgen-openai-compatible-api /bin/bash

ps:
	docker-compose ps

restart:
	docker-compose restart

# Installation
install-deps:
	@echo "Installing Python dependencies with uv..."
	uv sync

install-local:
	@echo "Installing package in development mode..."
	uv sync

# Quick commands
up: run
down: stop
rebuild: build-no-cache run
