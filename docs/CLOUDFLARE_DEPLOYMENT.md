# Cloudflare Deployment Guide for pappas.work

Complete guide for deploying QFZZ to your custom domain with Cloudflare.

## Overview

Your domain `pappas.work` with Cloudflare DNS provides excellent capabilities for hosting QFZZ:

✅ **Benefits**:
- **Free SSL/TLS** - Automatic HTTPS certificates
- **Global CDN** - Fast content delivery worldwide
- **DDoS Protection** - Built-in security
- **DNS Management** - Easy subdomain configuration
- **Page Rules** - Custom routing and caching
- **Analytics** - Traffic insights

## Quick Deploy

### Option 1: Cloudflare Pages (Static Frontend)

Best for the React frontend with API proxy.

```bash
# Build frontend
cd frontend
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy build --project-name=qfzz
```

### Option 2: Full Stack on VPS + Cloudflare

Recommended for complete QFZZ deployment.

## Architecture

```
pappas.work (Cloudflare DNS)
    │
    ├─ www.pappas.work → Main site
    ├─ app.pappas.work → QFZZ Web App
    ├─ api.pappas.work → API Server
    ├─ stream.pappas.work → Icecast Stream
    └─ docs.pappas.work → Documentation
```

## Step 1: Server Setup

### Get a VPS

Choose a provider:
- **DigitalOcean**: $6/month droplet
- **Vultr**: $6/month instance
- **Linode**: $5/month nanode
- **AWS EC2**: t2.micro (free tier)

### Install Requirements

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Clone QFZZ
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ
```

## Step 2: Cloudflare DNS Setup

### Add DNS Records

In Cloudflare Dashboard → DNS → Records:

```
Type    Name      Content           Proxy  TTL
----    ----      -------           -----  ---
A       @         YOUR_SERVER_IP    Yes    Auto
A       www       YOUR_SERVER_IP    Yes    Auto
A       app       YOUR_SERVER_IP    Yes    Auto
A       api       YOUR_SERVER_IP    Yes    Auto
A       stream    YOUR_SERVER_IP    Yes    Auto
A       docs      YOUR_SERVER_IP    Yes    Auto
```

**Note**: Orange cloud = Proxied (recommended for protection)

### SSL/TLS Settings

Go to **SSL/TLS** → **Overview**:
- Set to **Full (strict)** for best security
- Enable **Always Use HTTPS**

## Step 3: Configure QFZZ

### Create Production Config

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: qfzz-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/ssl:/etc/nginx/ssl:ro
      - certbot-data:/var/www/certbot
    depends_on:
      - qfzz-app
      - icecast
    networks:
      - qfzz-network
    restart: always

  # Let's Encrypt certificates
  certbot:
    image: certbot/certbot
    container_name: qfzz-certbot
    volumes:
      - ./config/ssl:/etc/letsencrypt
      - certbot-data:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d pappas.work -d www.pappas.work -d app.pappas.work -d api.pappas.work -d stream.pappas.work
    
  qfzz-app:
    environment:
      - DOMAIN=pappas.work
      - API_URL=https://api.pappas.work
      - STREAM_URL=https://stream.pappas.work/qfzz

volumes:
  certbot-data:

networks:
  qfzz-network:
    driver: bridge
```

### Nginx Configuration

Create `config/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=stream:10m rate=5r/s;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Main site - www.pappas.work
    server {
        listen 80;
        server_name pappas.work www.pappas.work;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name pappas.work www.pappas.work;

        ssl_certificate /etc/letsencrypt/live/pappas.work/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/pappas.work/privkey.pem;

        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }
    }

    # API - api.pappas.work
    server {
        listen 80;
        server_name api.pappas.work;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.pappas.work;

        ssl_certificate /etc/letsencrypt/live/pappas.work/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/pappas.work/privkey.pem;

        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://qfzz-app:8001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Stream - stream.pappas.work
    server {
        listen 80;
        server_name stream.pappas.work;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name stream.pappas.work;

        ssl_certificate /etc/letsencrypt/live/pappas.work/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/pappas.work/privkey.pem;

        location / {
            limit_req zone=stream burst=10 nodelay;
            
            proxy_pass http://icecast:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_buffering off;
        }
    }

    # Web App - app.pappas.work
    server {
        listen 80;
        server_name app.pappas.work;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name app.pappas.work;

        ssl_certificate /etc/letsencrypt/live/pappas.work/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/pappas.work/privkey.pem;

        location / {
            proxy_pass http://frontend:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## Step 4: Deploy

### Initial Deployment

```bash
# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Get SSL certificates
docker compose exec certbot certbot renew

# Reload nginx
docker compose restart nginx
```

### Verify Deployment

```bash
# Check services
docker compose ps

# Test endpoints
curl https://api.pappas.work/playlist.json
curl https://stream.pappas.work/status.xsl
```

## Step 5: Cloudflare Configuration

### Page Rules

Create these in Cloudflare Dashboard → Rules → Page Rules:

1. **Cache Everything** (for static assets)
   - URL: `app.pappas.work/static/*`
   - Settings: Cache Level = Cache Everything

2. **Bypass Cache** (for API)
   - URL: `api.pappas.work/*`
   - Settings: Cache Level = Bypass

3. **WebSocket Support** (for real-time)
   - URL: `app.pappas.work/*`
   - Settings: WebSockets = On

### Security Settings

Go to **Security** → **Settings**:
- Security Level: Medium
- Bot Fight Mode: On
- Challenge Passage: 30 minutes

### Firewall Rules

Create rule to protect API:
```
(http.request.uri.path contains "/admin" and ip.geoip.country ne "US")
```
Action: Block

## Step 6: Monitoring

### Cloudflare Analytics

View in Dashboard → Analytics:
- Traffic overview
- Security events
- Performance metrics

### Application Monitoring

```bash
# Check health
curl https://api.pappas.work/health

# View logs
docker compose logs -f qfzz-app
```

## Automated Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to pappas.work

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/qfzz
            git pull
            docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Custom Domain Features

### Email Setup

Use Cloudflare Email Routing:
1. Go to **Email** → **Email Routing**
2. Add destination address
3. Create routing rules:
   - `contact@pappas.work` → your-email@gmail.com
   - `admin@pappas.work` → your-email@gmail.com

### Subdomains

Add more as needed:
- `beta.pappas.work` - Testing environment
- `admin.pappas.work` - Admin panel
- `metrics.pappas.work` - Grafana dashboard

## SSL Certificate Renewal

Certificates auto-renew. To manually renew:

```bash
docker compose run --rm certbot renew
docker compose restart nginx
```

## Troubleshooting

### Check DNS Propagation

```bash
dig pappas.work
nslookup app.pappas.work
```

### SSL Issues

```bash
# Test SSL
curl -I https://pappas.work

# Check certificate
openssl s_client -connect pappas.work:443
```

### Cloudflare Cache

Clear cache in Dashboard → Caching → Configuration → Purge Everything

## Cost Estimate

**Monthly Costs**:
- Domain: Already purchased
- Cloudflare: Free (Pro optional: $20/month)
- VPS: $5-10/month
- **Total: ~$5-10/month**

## Production Checklist

- [ ] DNS records configured
- [ ] SSL certificates obtained
- [ ] Services deployed
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backups automated
- [ ] Firewall rules set
- [ ] Rate limiting enabled
- [ ] Error pages customized

## Support

For deployment issues:
- Cloudflare Docs: https://developers.cloudflare.com/
- QFZZ Docker Guide: `docs/DOCKER_GUIDE.md`
- Community Forum: https://community.cloudflare.com/

---

**Your domain `pappas.work` is perfect for hosting QFZZ!** Follow this guide to get your production deployment live.
