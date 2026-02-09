# Deployment Guide

This guide covers deploying the BharatGen OpenAI-Compatible API to a remote server.

## Prerequisites

- Remote server with Docker and Docker Compose installed
- SSH access to the server
- Domain name (optional, for HTTPS)
- SSL certificate (optional, for HTTPS with nginx)

## Deployment Options

### Option 1: Docker Compose (Recommended)

This is the simplest method for production deployment.

#### Step 1: Prepare Your Server

```bash
# SSH into your server
ssh user@your-server.com

# Install Docker and Docker Compose if not already installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Transfer Files to Server

```bash
# From your local machine
scp -r bharatgen-param-17b user@your-server.com:~/

# Or use git
ssh user@your-server.com
git clone <your-repo-url>
cd bharatgen-param-17b
```

#### Step 3: Configure Environment

```bash
# On the remote server
cd bharatgen-param-17b
cp .env.example .env

# Edit environment variables
nano .env
```

Update `.env` with production values:
```bash
BHARATGEN_BASE_URL=https://your-gradio-instance.com/gradio_api
BHARATGEN_API_KEYS=sk-prod-key-1,sk-prod-key-2,sk-prod-key-3
BHARATGEN_PORT=8000
BHARATGEN_HOST=0.0.0.0
```

#### Step 4: Deploy

```bash
# Build and start the container
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### Step 5: Test the Deployment

```bash
# From the server
curl http://localhost:8000/health

# From your local machine (replace with your server IP/domain)
curl http://your-server.com:8000/health
```

### Option 2: Docker with Nginx Reverse Proxy (Production with HTTPS)

For production with SSL/HTTPS, use nginx as a reverse proxy.

#### Step 1: Create nginx configuration

```bash
# Create docker-compose.prod.yml
```

See the `docker-compose.prod.yml` file in this directory.

#### Step 2: Set up SSL certificates

```bash
# Using Let's Encrypt with Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.yourdomain.com
```

#### Step 3: Deploy with nginx

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Cloud Platforms

#### AWS ECS/Fargate

1. Push image to ECR:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag bharatgen-openai-compatible-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/bharatgen-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/bharatgen-api:latest
```

2. Create ECS task definition with environment variables
3. Create ECS service with load balancer

#### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/bharatgen-api

# Deploy to Cloud Run
gcloud run deploy bharatgen-api \
  --image gcr.io/<project-id>/bharatgen-api \
  --platform managed \
  --port 8000 \
  --set-env-vars BHARATGEN_API_KEYS=sk-prod-key \
  --allow-unauthenticated
```

#### DigitalOcean App Platform

1. Push code to GitHub
2. Create new app in DigitalOcean
3. Connect GitHub repository
4. Configure environment variables in the dashboard
5. Deploy

#### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

## Production Best Practices

### 1. Security

```bash
# Use strong API keys (32+ characters)
openssl rand -hex 32  # Generate secure key

# Update .env
BHARATGEN_API_KEYS=generated-secure-key-here
```

### 2. Monitoring

Add health checks to your deployment:

```yaml
# In docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. Logging

```bash
# View logs
docker-compose logs -f

# Save logs to file
docker-compose logs > logs.txt

# Use log rotation
docker-compose --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 up -d
```

### 4. Auto-restart

Ensure the container restarts on failure:

```yaml
services:
  bharatgen-openai-compatible-api:
    restart: unless-stopped
```

### 5. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 6. Resource Limits

```yaml
# In docker-compose.yml
services:
  bharatgen-openai-compatible-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Updating the Deployment

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or for zero-downtime updates
docker-compose build
docker-compose up -d --no-deps --build bharatgen-openai-compatible-api
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
docker-compose ps
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :8000

# Change port in .env or docker-compose.yml
```

### Out of memory
```bash
# Check container stats
docker stats

# Increase memory limits in docker-compose.yml
```

### Can't connect from external
```bash
# Check firewall
sudo ufw status

# Check if container is listening
docker exec <container-id> netstat -tlnp
```

## Monitoring and Maintenance

### Set up monitoring with Uptime Kuma

```bash
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

### Backup strategy

```bash
# Backup script
#!/bin/bash
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz bharatgen-param-17b/
docker-compose up -d
```

## Performance Optimization

1. **Use a CDN** for static assets
2. **Enable HTTP/2** with nginx
3. **Rate limiting** with nginx or API gateway
4. **Caching** responses when appropriate
5. **Load balancing** for multiple instances

## Scaling

For high traffic, run multiple instances:

```yaml
# docker-compose.scale.yml
services:
  bharatgen-openai-compatible-api:
    deploy:
      replicas: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - bharatgen-openai-compatible-api
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Run health check: `curl http://localhost:8000/health`
- Run test suite: `./test_docker_endpoints.sh`
