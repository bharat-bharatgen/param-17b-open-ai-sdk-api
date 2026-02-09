# Quick Command Reference

## Build Commands

### Using build.sh script
```bash
# Basic build
./build.sh

# Build without cache
./build.sh --no-cache

# Build with custom tag
./build.sh --tag v1.0.0

# Build with custom tag and no cache
./build.sh --no-cache --tag v1.0.0
```

### Using Makefile
```bash
# Build with cache
make build

# Build without cache (clean build)
make build-no-cache

# Rebuild and run
make rebuild
```

### Using Docker directly
```bash
# Basic build
docker build -t bharatgen-openai-compatible-api:latest .

# Build without cache
docker build --no-cache -t bharatgen-openai-compatible-api:latest .

# Build with custom tag
docker build -t bharatgen-openai-compatible-api:v1.0.0 .
```

### Using docker-compose
```bash
# Build (or rebuild) services
docker-compose build

# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build bharatgen-openai-compatible-api
```

## Run Commands

### Development
```bash
# Using Makefile
make run              # Run in background
make run-dev          # Run in foreground (see logs)

# Using docker-compose
docker-compose up     # Foreground
docker-compose up -d  # Background (-d = detached)

# Using Docker directly
docker run -p 8000:8000 \
  -e BHARATGEN_API_KEYS=sk-test-key \
  bharatgen-openai-compatible-api:latest
```

### Production (Simple - No Nginx)
```bash
# Using Makefile
make run-simple

# Using docker-compose
docker-compose -f docker-compose.simple.yml up -d
```

### Production (With Nginx)
```bash
# Using Makefile
make run-prod

# Using docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Stop Commands

```bash
# Using Makefile
make stop         # Stop default config
make stop-all     # Stop all configurations

# Using docker-compose
docker-compose down                                    # Stop default
docker-compose -f docker-compose.simple.yml down      # Stop simple
docker-compose -f docker-compose.prod.yml down        # Stop prod

# Stop and remove volumes
docker-compose down -v
```

## Test Commands

```bash
# Using Makefile
make test         # Test Docker deployment

# Using test script directly
./test_docker_endpoints.sh 8000

# Manual curl test
curl http://localhost:8000/health
```

## Logs Commands

```bash
# Using Makefile
make logs         # Follow default logs
make logs-prod    # Follow production logs

# Using docker-compose
docker-compose logs                    # View all logs
docker-compose logs -f                 # Follow logs (live)
docker-compose logs --tail=100         # Last 100 lines
docker-compose logs bharatgen-openai-compatible-api  # Specific service

# Using Docker directly
docker logs <container-id>
docker logs -f <container-id>
docker logs --tail=100 <container-id>
```

## Container Management

```bash
# Using Makefile
make ps           # List containers
make shell        # Get shell in container
make restart      # Restart containers

# Using docker-compose
docker-compose ps                      # List containers
docker-compose restart                 # Restart all
docker-compose exec bharatgen-openai-compatible-api /bin/bash  # Shell

# Using Docker directly
docker ps                              # List running containers
docker exec -it <container-id> /bin/bash  # Shell into container
```

## Cleanup Commands

```bash
# Using Makefile
make clean        # Remove containers and images
make clean-all    # Remove everything (containers, images, volumes)

# Using docker-compose
docker-compose down           # Stop and remove containers
docker-compose down -v        # Also remove volumes
docker-compose down --rmi all # Also remove images

# Using Docker directly
docker rm <container-id>                    # Remove container
docker rmi bharatgen-openai-compatible-api  # Remove image
docker system prune -f                      # Clean up everything
```

## Deployment Commands

```bash
# Using deploy script
./deploy.sh production

# Using Makefile
make deploy
```

## Push to Registry

```bash
# Using Makefile (interactive)
make push

# Manual push to Docker Hub
docker login
docker tag bharatgen-openai-compatible-api:latest username/bharatgen-openai-compatible-api:latest
docker push username/bharatgen-openai-compatible-api:latest

# Push to private registry
docker tag bharatgen-openai-compatible-api:latest registry.example.com/bharatgen-openai-compatible-api:latest
docker push registry.example.com/bharatgen-openai-compatible-api:latest

# Push to Google Container Registry
docker tag bharatgen-openai-compatible-api:latest gcr.io/PROJECT-ID/bharatgen-openai-compatible-api:latest
docker push gcr.io/PROJECT-ID/bharatgen-openai-compatible-api:latest

# Push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag bharatgen-openai-compatible-api:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bharatgen-openai-compatible-api:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bharatgen-openai-compatible-api:latest
```

## Local Python Development

```bash
# Using Makefile
make install-deps    # Install dependencies with uv
make install-local   # Install in development mode

# Manual with uv
uv sync

# Run server locally (no Docker)
python -m bharatgen_openai.server
```

## Quick Reference Table

| Task | Makefile | docker-compose | Script |
|------|----------|----------------|--------|
| **Build** | `make build` | `docker-compose build` | `./build.sh` |
| **Run Dev** | `make run` | `docker-compose up -d` | - |
| **Run Prod** | `make run-simple` | `docker-compose -f docker-compose.simple.yml up -d` | - |
| **Stop** | `make stop` | `docker-compose down` | - |
| **Test** | `make test` | - | `./test_docker_endpoints.sh 8000` |
| **Logs** | `make logs` | `docker-compose logs -f` | - |
| **Clean** | `make clean` | `docker-compose down -v` | - |
| **Deploy** | `make deploy` | - | `./deploy.sh production` |

## Environment Variables

```bash
# Set before running
export BHARATGEN_BASE_URL="https://your-gradio-instance.com/gradio_api"
export BHARATGEN_API_KEYS="sk-prod-key-1,sk-prod-key-2"
export BHARATGEN_PORT="8000"

# Or use .env file
cp .env.example .env
nano .env
```

## Troubleshooting Commands

```bash
# Check container status
docker ps -a

# View container resource usage
docker stats

# Inspect container
docker inspect <container-id>

# Check logs for errors
docker-compose logs | grep -i error

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Test connectivity
curl -v http://localhost:8000/health

# Check port availability
lsof -i :8000
```
