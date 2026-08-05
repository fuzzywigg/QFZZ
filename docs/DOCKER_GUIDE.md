# Docker Deployment Guide

Complete guide for deploying QFZZ using Docker and Docker Compose.

## Overview

QFZZ provides a comprehensive Docker setup with:
- **Multi-stage builds** for development, testing, and production
- **Docker Compose** orchestration for all services
- **Optional services** via profiles (frontend, monitoring)
- **Production-ready** configuration with health checks and restart policies

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    QFZZ Stack                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Icecast  │  │   QFZZ   │  │ Frontend │           │
│  │  Server   │◄─┤   App    │◄─┤   (opt)  │           │
│  │   :8000   │  │  :8001   │  │  :3001   │           │
│  └───────────┘  └──────────┘  └──────────┘           │
│        │             │              │                  │
│        ▼             ▼              ▼                  │
│  ┌──────────────────────────────────────┐            │
│  │         Network: qfzz-network         │            │
│  └──────────────────────────────────────┘            │
│        │             │                                 │
│        ▼             ▼                                 │
│  ┌───────────┐  ┌──────────┐  ┌──────────┐          │
│  │ PostgreSQL│  │  Redis   │  │Prometheus│          │
│  │   :5432   │  │  :6379   │  │  :9090   │          │
│  └───────────┘  └──────────┘  └──────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Docker** (20.10+)
   ```bash
   # Check version
   docker --version
   
   # Install: https://docs.docker.com/get-docker/
   ```

2. **Docker Compose** (2.0+)
   ```bash
   # Check version
   docker compose version
   
   # Usually installed with Docker Desktop
   ```

### One-Command Start

```bash
./scripts/docker-start.sh
```

This interactive script will:
1. Check prerequisites
2. Create necessary directories
3. Set up `.env` file
4. Let you choose which services to start
5. Build and launch the stack

### Manual Start

```bash
# 1. Create environment file
cp .env.example .env
# Edit .env and add your API keys

# 2. Build images
docker compose build

# 3. Start core services
docker compose up -d

# 4. View logs
docker compose logs -f

# 5. Check status
docker compose ps
```

## Services

### Core Services (Always Running)

#### 1. Icecast Server
- **Port**: 8000
- **Purpose**: Production streaming server
- **URL**: http://localhost:8000
- **Stream**: http://localhost:8000/qfzz
- **Admin**: http://localhost:8000/admin/ (admin/hackme)

#### 2. QFZZ Application
- **Port**: 8001 (API), 3000 (alt)
- **Purpose**: Main radio application
- **API**: http://localhost:8001/playlist.json
- **Health**: http://localhost:8001/status

#### 3. PostgreSQL
- **Port**: 5432
- **Purpose**: Production database
- **Database**: qfzz
- **User**: qfzz / qfzz_password_change_me

#### 4. Redis
- **Port**: 6379
- **Purpose**: Caching and session storage
- **Optional**: Not used yet, available for future

### Optional Services (Use Profiles)

#### Frontend (React UI)
```bash
docker compose --profile frontend up -d
```
- **Port**: 3001
- **URL**: http://localhost:3001

#### Monitoring Stack
```bash
docker compose --profile monitoring up -d
```
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002 (admin/admin)

#### All Services
```bash
docker compose --profile frontend --profile monitoring up -d
```

## Configuration

### Environment Variables

Create `.env` file with:

```env
# LLM API Keys
GOOGLE_AI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Icecast
ICECAST_HOST=icecast
ICECAST_PORT=8000
ICECAST_PASSWORD=hackme
ICECAST_MOUNT=/qfzz

# Application
QFZZ_STATION_NAME=QFZZ Prime
QFZZ_ENABLE_BLOCKCHAIN=true
QFZZ_ENABLE_ICECAST=true

# Database
POSTGRES_PASSWORD=change_me_in_production
```

### Volume Mounts

The stack persists data in:
- `qfzz_audio_content/` - Audio files
- `honeycomb/` - Application state
- `qfzz_ledger.json` - Blockchain ledger
- `qfzz_knowledge_graph.json` - Knowledge graph
- Docker volumes:
  - `postgres-data` - Database
  - `redis-data` - Cache
  - `icecast-logs` - Streaming logs
  - `qfzz-logs` - Application logs

## Common Operations

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### Restart Single Service
```bash
docker compose restart qfzz-app
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f qfzz-app

# Last 100 lines
docker compose logs --tail=100 qfzz-app
```

### Shell Access
```bash
# QFZZ app container
docker compose exec qfzz-app bash

# PostgreSQL
docker compose exec postgres psql -U qfzz
```

### Update Images
```bash
docker compose pull
docker compose up -d
```

### Rebuild After Code Changes
```bash
docker compose build qfzz-app
docker compose up -d qfzz-app
```

## Development

### Development Mode

Use the development target for hot-reloading:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Or build development image:
```bash
docker build --target development -t qfzz:dev .
docker run -it -v $(pwd):/app -p 8001:8001 qfzz:dev
```

### Running Tests

```bash
# Run tests in container
docker compose run --rm qfzz-app python -m unittest discover tests

# Or use test stage
docker build --target testing -t qfzz:test .
docker run --rm qfzz:test
```

## Production Deployment

### Security Checklist

1. **Change all passwords**:
   - `.env`: All API keys and passwords
   - `config/icecast.xml`: source-password, admin-password
   - `docker-compose.yml`: PostgreSQL password

2. **Use secrets management**:
   ```bash
   # Docker Swarm secrets
   echo "my_secret_key" | docker secret create api_key -
   ```

3. **Enable HTTPS**:
   - Add reverse proxy (nginx/traefik)
   - Configure SSL certificates
   - Update Icecast for HTTPS

4. **Resource Limits**:
   ```yaml
   services:
     qfzz-app:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
           reservations:
             cpus: '0.5'
             memory: 512M
   ```

### Scaling

Scale specific services:
```bash
docker compose up -d --scale qfzz-app=3
```

### Production Compose

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  qfzz-app:
    image: qfzz:latest
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Use it:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring

### Health Checks

All services have health checks:
```bash
docker compose ps
```

Look for "healthy" status.

### Logs

Structured logging to files:
```bash
# Application logs
docker compose exec qfzz-app tail -f /app/logs/qfzz.log

# Icecast logs
docker compose exec icecast tail -f /var/log/icecast2/error.log
```

### Metrics (with monitoring profile)

1. **Prometheus**: http://localhost:9090
   - Metrics collection
   - Query interface

2. **Grafana**: http://localhost:3002
   - Dashboards
   - Alerts
   - Login: admin/admin

## Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs

# Check individual service
docker compose logs qfzz-app

# Validate compose file
docker compose config
```

### Connection refused

```bash
# Check if services are running
docker compose ps

# Check network
docker network inspect qfzz_qfzz-network

# Test connectivity
docker compose exec qfzz-app ping icecast
```

### Database issues

```bash
# Reset database
docker compose down -v
docker compose up -d postgres

# Check database
docker compose exec postgres psql -U qfzz -d qfzz
```

### Icecast not streaming

```bash
# Check Icecast logs
docker compose logs icecast

# Verify config
docker compose exec icecast cat /etc/icecast2/icecast.xml

# Test connection
curl http://localhost:8000/status.xsl
```

### Container disk space

```bash
# Check space
docker system df

# Clean up
docker system prune -a
docker volume prune
```

### Permission errors

```bash
# Fix ownership (Linux)
sudo chown -R $USER:$USER qfzz_audio_content honeycomb

# Or run as root (not recommended)
docker compose run --user root qfzz-app bash
```

## Backup and Restore

### Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup volumes
docker run --rm \
  -v qfzz_postgres-data:/data \
  -v "$BACKUP_DIR":/backup \
  alpine tar czf /backup/postgres.tar.gz /data

# Backup files
tar czf "$BACKUP_DIR/audio.tar.gz" qfzz_audio_content/
tar czf "$BACKUP_DIR/state.tar.gz" honeycomb/ *.json

echo "Backup complete: $BACKUP_DIR"
```

### Restore

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

# Stop services
docker compose down

# Restore volumes
docker run --rm \
  -v qfzz_postgres-data:/data \
  -v "$BACKUP_DIR":/backup \
  alpine tar xzf /backup/postgres.tar.gz -C /

# Restore files
tar xzf "$BACKUP_DIR/audio.tar.gz"
tar xzf "$BACKUP_DIR/state.tar.gz"

# Start services
docker compose up -d

echo "Restore complete"
```

## Performance Tuning

### Build Optimization

```dockerfile
# Use BuildKit
DOCKER_BUILDKIT=1 docker build .

# Multi-stage caching
docker build --target base -t qfzz:base .
docker build --target production --cache-from qfzz:base .
```

### Runtime Optimization

```yaml
# docker-compose.yml additions
services:
  qfzz-app:
    # CPU shares
    cpu_shares: 1024
    
    # Memory limits
    mem_limit: 2g
    memswap_limit: 2g
    
    # OOM handling
    oom_kill_disable: false
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Build image
        run: docker build .
      - name: Run tests
        run: docker build --target testing .
```

### GitLab CI

```yaml
# .gitlab-ci.yml
docker-build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME
```

## Resources

- **Docker Docs**: https://docs.docker.com/
- **Compose Docs**: https://docs.docker.com/compose/
- **Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **QFZZ Repo**: https://github.com/fuzzywigg/QFZZ

## Support

For issues with:
- **Docker setup**: Check this guide first
- **QFZZ application**: See main README.md
- **Icecast**: See ICECAST_GUIDE.md

Open an issue on GitHub: https://github.com/fuzzywigg/QFZZ/issues
