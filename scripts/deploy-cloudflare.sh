#!/usr/bin/env bash
# Quick deployment script for pappas.work

set -e

echo "========================================"
echo "QFZZ Deployment to pappas.work"
echo "========================================"
echo ""

# Check if running on server
if [ -z "$SERVER_IP" ]; then
    echo "This script should be run on your VPS server."
    echo ""
    echo "First-time setup:"
    echo "1. Get a VPS (DigitalOcean, Vultr, etc.)"
    echo "2. SSH to server: ssh root@YOUR_SERVER_IP"
    echo "3. Clone repo: git clone https://github.com/fuzzywigg/QFZZ.git"
    echo "4. Run: cd QFZZ && ./scripts/deploy-cloudflare.sh"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker compose &> /dev/null; then
    apt-get update
    apt-get install -y docker-compose-plugin
fi

# Configure environment
echo ""
echo "Configuring environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file with your API keys!"
    read -p "Press Enter after editing .env..."
fi

# Set domain
export DOMAIN="pappas.work"
echo "DOMAIN=$DOMAIN" >> .env

# Create directories
mkdir -p config/ssl logs

# Deploy services
echo ""
echo "Starting services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services
echo ""
echo "Waiting for services to start..."
sleep 10

# Check health
echo ""
echo "Checking service health..."
docker compose ps

# Get SSL certificates
echo ""
echo "Setting up SSL certificates..."
read -p "Enter your email for Let's Encrypt: " EMAIL

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d pappas.work \
    -d www.pappas.work \
    -d app.pappas.work \
    -d api.pappas.work \
    -d stream.pappas.work

# Reload nginx
docker compose restart nginx

# Print summary
echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Your QFZZ instance is now live at:"
echo ""
echo "  Main Site:  https://pappas.work"
echo "  Web App:    https://app.pappas.work"
echo "  API:        https://api.pappas.work"
echo "  Stream:     https://stream.pappas.work/qfzz"
echo ""
echo "Next steps:"
echo "1. Configure DNS in Cloudflare dashboard"
echo "2. Wait for DNS propagation (5-10 minutes)"
echo "3. Test endpoints above"
echo ""
echo "View logs: docker compose logs -f"
echo "Stop services: docker compose down"
echo ""
