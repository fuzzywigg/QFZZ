# QFZZ Deployment Guide

Complete guide to deploying QFZZ in production environments, including Firebase, AWS, Google Cloud, Azure, Docker/Kubernetes, self-hosting, monitoring, scaling, and security hardening.

## Table of Contents

- [Deployment Overview](#deployment-overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Firebase Deployment](#firebase-deployment)
- [AWS Deployment](#aws-deployment)
- [Google Cloud Deployment](#google-cloud-deployment)
- [Azure Deployment](#azure-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Self-Hosting](#self-hosting)
- [Production Best Practices](#production-best-practices)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling](#scaling)
- [Security Hardening](#security-hardening)

## Deployment Overview

QFZZ can be deployed on multiple platforms:

```
┌─────────────────────────────────────────────────┐
│          QFZZ Application                       │
├─────────────────────────────────────────────────┤
│  Platform Options:                              │
│  • Firebase (Serverless)                        │
│  • AWS (EC2, Lambda, ECS)                       │
│  • Google Cloud (Cloud Run, GKE)                │
│  • Azure (App Service, AKS)                     │
│  • Docker (Containers)                          │
│  • Kubernetes (Orchestration)                   │
│  • Self-Hosted (On-Premises)                    │
└─────────────────────────────────────────────────┘
```

### Deployment Architecture

```
Internet Traffic
      ↓
   Load Balancer
      ↓
   API Gateway
      ↓
┌─────────────────┐
│  QFZZ Instances │ (Multiple replicas)
│  - DJ Engine    │
│  - Blockchain   │
│  - Edge Opt.    │
│  - Datasets     │
└─────────────────┘
      ↓
┌─────────────────┐
│ Data Layer      │
│ - Cache (Redis) │
│ - Database      │
│ - Storage       │
└─────────────────┘
```

## Pre-Deployment Checklist

### Requirements Verification

- [ ] Python 3.8+ installed on target platform
- [ ] All dependencies listed in requirements.txt
- [ ] API keys and credentials prepared
- [ ] SSL/TLS certificates acquired
- [ ] Database credentials configured
- [ ] Backup strategy defined
- [ ] Monitoring tools configured

### Configuration Verification

- [ ] Production configuration file created
- [ ] Environment variables documented
- [ ] Security settings reviewed
- [ ] Performance settings optimized
- [ ] Logging configured
- [ ] Error handling verified
- [ ] Rate limiting configured

### Testing Verification

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Security audit completed
- [ ] Backup/restore tested
- [ ] Failover tested
- [ ] Performance baselines established

### Security Checklist

- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] API authentication implemented
- [ ] Rate limiting enabled
- [ ] Secrets management configured
- [ ] Audit logging enabled
- [ ] Intrusion detection configured

## Firebase Deployment

### Firebase Setup

#### Prerequisites

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# List available projects
firebase projects:list
```

#### Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a new project"
3. Name your project: "qfzz-station"
4. Create project

#### Initialize Firebase in Project

```bash
# In your QFZZ project directory
firebase init

# Select options:
# ✓ Firestore
# ✓ Functions
# ✓ Hosting
# ✓ Storage
```

### Firebase Configuration

#### firebaserc Configuration

Create `.firebaserc`:

```json
{
  "projects": {
    "default": "qfzz-station",
    "production": "qfzz-production"
  }
}
```

#### Cloud Functions Deployment

Create `functions/index.js`:

```javascript
const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp();

// QFZZ Station endpoint
exports.generatePlaylist = functions.https.onCall(async (data, context) => {
    // Verify authentication
    if (!context.auth) {
        throw new functions.https.HttpsError('unauthenticated', 'User not authenticated');
    }
    
    const userId = context.auth.uid;
    const preferences = data.preferences;
    
    // Call Python QFZZ backend
    // Implementation varies based on your setup
    
    return {
        status: 'success',
        playlist: []
    };
});

// Update user profile
exports.updateUserProfile = functions.https.onCall(async (data, context) => {
    if (!context.auth) {
        throw new functions.https.HttpsError('unauthenticated', 'User not authenticated');
    }
    
    const userId = context.auth.uid;
    const db = admin.firestore();
    
    await db.collection('users').doc(userId).set(data, { merge: true });
    
    return { status: 'success' };
});
```

#### Firestore Database Rules

Create `firestore.rules`:

```
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    // User data
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    
    // Playlists
    match /playlists/{playlistId} {
      allow read: if request.auth.uid == resource.data.owner_id;
      allow write: if request.auth.uid == resource.data.owner_id;
    }
    
    // Public content
    match /content/{contentId} {
      allow read: if true;
      allow write: if request.auth.uid == resource.data.creator_id;
    }
  }
}
```

#### Storage Rules

Create `storage.rules`:

```
rules_version = '2';

service firebase.storage {
  match /b/{bucket}/o {
    // User uploads
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth.uid == userId;
    }
    
    // Public content
    match /content/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth.uid == request.resource.metadata.creator_id;
    }
  }
}
```

### Deploying to Firebase

```bash
# Deploy functions
firebase deploy --only functions

# Deploy Firestore rules
firebase deploy --only firestore:rules

# Deploy storage rules
firebase deploy --only storage

# Deploy everything
firebase deploy

# View deployment
firebase open console
```

### Environment Variables for Firebase

Create `.env.firebase`:

```bash
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=qfzz-station.firebaseapp.com
FIREBASE_PROJECT_ID=qfzz-station
FIREBASE_STORAGE_BUCKET=qfzz-station.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
```

## AWS Deployment

### Option 1: AWS Lambda

#### Prerequisites

```bash
# Install SAM CLI (Serverless Application Model)
brew install aws-sam-cli

# Configure AWS credentials
aws configure
```

#### SAM Template

Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: QFZZ Radio Station

Globals:
  Function:
    Runtime: python3.10
    Timeout: 30
    Environment:
      Variables:
        STATION_ID: !Ref StationId
        ENABLE_BLOCKCHAIN: 'true'

Parameters:
  StationId:
    Type: String
    Default: qfzz-lambda-station

Resources:
  # Lambda Function
  QFZZFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: qfzz-station
      CodeUri: src/
      Handler: app.lambda_handler
      Events:
        GeneratePlaylist:
          Type: Api
          Properties:
            RestApiId: !Ref QFZZApi
            Path: /playlist
            Method: POST
        GetStats:
          Type: Api
          Properties:
            RestApiId: !Ref QFZZApi
            Path: /stats
            Method: GET
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref StationsTable
        - S3CrudPolicy:
            BucketName: !Ref DataBucket
  
  # API Gateway
  QFZZApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: qfzz-api
      StageName: prod
      Auth:
        DefaultAuthorizer: QFZZAuthorizer
        Authorizers:
          QFZZAuthorizer:
            FunctionArn: !GetAtt AuthorizerFunction.Arn
  
  # DynamoDB Table
  StationsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: qfzz-stations
      AttributeDefinitions:
        - AttributeName: station_id
          AttributeType: S
      KeySchema:
        - AttributeName: station_id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
  
  # S3 Bucket
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: qfzz-data-bucket
      VersioningConfiguration:
        Status: Enabled
  
  # RDS Database
  QFZZDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      Engine: postgres
      EngineVersion: '14'
      DBInstanceClass: db.t3.micro
      AllocatedStorage: 20
      StorageType: gp2
      DBName: qfzz_db
      MasterUsername: admin
      MasterUserPassword: !Sub '{{resolve:secretsmanager:qfzz/db:SecretString:password}}'

Outputs:
  APIEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${QFZZApi}.execute-api.${AWS::Region}.amazonaws.com/prod/'
  
  DatabaseEndpoint:
    Description: RDS database endpoint
    Value: !GetAtt QFZZDatabase.Endpoint.Address
  
  DataBucketName:
    Description: S3 bucket for data storage
    Value: !Ref DataBucket
```

Deploy SAM template:

```bash
# Build SAM application
sam build

# Deploy with guided setup
sam deploy --guided

# View deployed stack
aws cloudformation describe-stacks --stack-name qfzz-station
```

### Option 2: AWS ECS (Elastic Container Service)

#### ECS Cluster Creation

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name qfzz-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Run service
aws ecs create-service \
  --cluster qfzz-cluster \
  --service-name qfzz-service \
  --task-definition qfzz-task \
  --desired-count 3
```

#### Task Definition

Create `task-definition.json`:

```json
{
  "family": "qfzz-task",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "qfzz",
      "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/qfzz:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "QFZZ_STATION_ID",
          "value": "ecs-station"
        },
        {
          "name": "QFZZ_ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "FIREBASE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:qfzz/firebase-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/qfzz",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024"
}
```

### AWS Configuration

Create `aws_config.py`:

```python
import boto3

class AWSConfig:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.secrets_manager = boto3.client('secretsmanager')
    
    def get_secret(self, secret_name):
        """Retrieve secret from AWS Secrets Manager."""
        response = self.secrets_manager.get_secret_value(
            SecretId=secret_name
        )
        return response['SecretString']
    
    def upload_to_s3(self, bucket, key, data):
        """Upload data to S3."""
        self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=data
        )
    
    def store_station_config(self, station_id, config_data):
        """Store station config in DynamoDB."""
        table = self.dynamodb.Table('qfzz-stations')
        table.put_item(Item={
            'station_id': station_id,
            'config': config_data
        })

aws_config = AWSConfig()
```

## Google Cloud Deployment

### Google Cloud Setup

#### Prerequisites

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize Google Cloud
gcloud init

# Set project
gcloud config set project qfzz-project
```

### Option 1: Cloud Run

#### Create Cloud Run Service

```bash
# Build Docker image
gcloud builds submit --tag gcr.io/qfzz-project/qfzz-station

# Deploy to Cloud Run
gcloud run deploy qfzz-station \
  --image gcr.io/qfzz-project/qfzz-station \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars QFZZ_ENVIRONMENT=production
```

#### Cloud Run Configuration

Create `app.yaml`:

```yaml
runtime: python310
env: standard

env_variables:
  QFZZ_STATION_NAME: "Cloud Run Station"
  QFZZ_ENVIRONMENT: "production"

handlers:
- url: /.*
  script: auto
```

Deploy with `app.yaml`:

```bash
gcloud app deploy app.yaml
```

### Option 2: Google Kubernetes Engine (GKE)

#### Create GKE Cluster

```bash
# Create cluster
gcloud container clusters create qfzz-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-1

# Get credentials
gcloud container clusters get-credentials qfzz-cluster \
  --zone us-central1-a
```

#### Deploy to GKE

Create `gke-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qfzz-station
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qfzz
  template:
    metadata:
      labels:
        app: qfzz
    spec:
      containers:
      - name: qfzz
        image: gcr.io/qfzz-project/qfzz-station:latest
        ports:
        - containerPort: 8000
        env:
        - name: QFZZ_ENVIRONMENT
          value: "production"
        - name: QFZZ_STATION_NAME
          value: "GKE Station"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

---
apiVersion: v1
kind: Service
metadata:
  name: qfzz-service
spec:
  selector:
    app: qfzz
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:

```bash
# Apply deployment
kubectl apply -f gke-deployment.yaml

# View service
kubectl get service qfzz-service

# Check pods
kubectl get pods
```

## Azure Deployment

### Azure Setup

#### Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create \
  --name qfzz-rg \
  --location eastus
```

### Option 1: Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name qfzz-plan \
  --resource-group qfzz-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group qfzz-rg \
  --plan qfzz-plan \
  --name qfzz-station \
  --runtime "python|3.10"

# Deploy from Git
az webapp deployment source config-zip \
  --resource-group qfzz-rg \
  --name qfzz-station \
  --src qfzz-app.zip
```

### Option 2: Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create \
  --resource-group qfzz-rg \
  --name qfzz-cluster \
  --node-count 3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials \
  --resource-group qfzz-rg \
  --name qfzz-cluster

# Deploy to AKS
kubectl apply -f aks-deployment.yaml
```

Create `aks-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qfzz-station
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qfzz
  template:
    metadata:
      labels:
        app: qfzz
    spec:
      containers:
      - name: qfzz
        image: myacr.azurecr.io/qfzz:latest
        ports:
        - containerPort: 8000
        env:
        - name: QFZZ_ENVIRONMENT
          value: "production"
```

## Docker Deployment

### Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY qfzz/ ./qfzz/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 qfzz
USER qfzz

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "qfzz.server"]
```

### Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  qfzz-app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: qfzz-production
    environment:
      - QFZZ_STATION_ID=docker_prod
      - QFZZ_ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
      - DB_URL=postgresql://user:password@db:5432/qfzz
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - db
    restart: unless-stopped
    networks:
      - qfzz-network
    volumes:
      - qfzz-data:/data
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
  
  redis:
    image: redis:7-alpine
    container_name: qfzz-redis
    restart: unless-stopped
    networks:
      - qfzz-network
    volumes:
      - redis-data:/data
  
  db:
    image: postgres:14-alpine
    container_name: qfzz-db
    environment:
      - POSTGRES_DB=qfzz
      - POSTGRES_USER=qfzz_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped
    networks:
      - qfzz-network
    volumes:
      - postgres-data:/var/lib/postgresql/data
  
  nginx:
    image: nginx:alpine
    container_name: qfzz-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - qfzz-app
    restart: unless-stopped
    networks:
      - qfzz-network

volumes:
  qfzz-data:
  redis-data:
  postgres-data:

networks:
  qfzz-network:
    driver: bridge
```

Deploy Docker Compose:

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f qfzz-app

# Stop
docker-compose -f docker-compose.prod.yml down
```

## Kubernetes Deployment

### Production Kubernetes Manifest

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qfzz-station
  namespace: qfzz-prod
  labels:
    app: qfzz
    environment: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: qfzz
  template:
    metadata:
      labels:
        app: qfzz
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: qfzz-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: qfzz
        image: qfzz/qfzz:latest
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: QFZZ_ENVIRONMENT
          value: production
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: qfzz-secrets
              key: redis-url
        - name: DB_URL
          valueFrom:
            secretKeyRef:
              name: qfzz-secrets
              key: db-url
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /etc/qfzz
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: qfzz-config

---
apiVersion: v1
kind: Service
metadata:
  name: qfzz-service
  namespace: qfzz-prod
spec:
  type: LoadBalancer
  selector:
    app: qfzz
  ports:
  - protocol: TCP
    port: 80
    targetPort: http

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: qfzz-hpa
  namespace: qfzz-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: qfzz-station
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Deploy to Kubernetes:

```bash
# Create namespace
kubectl create namespace qfzz-prod

# Create secrets
kubectl create secret generic qfzz-secrets \
  --from-literal=redis-url=redis://redis:6379 \
  --from-literal=db-url=postgresql://user:pass@db:5432/qfzz \
  -n qfzz-prod

# Apply manifests
kubectl apply -f k8s/

# Verify deployment
kubectl get deployment -n qfzz-prod
kubectl get pods -n qfzz-prod
kubectl get svc -n qfzz-prod
```

## Self-Hosting

### On-Premises Setup

#### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 8+ cores |
| RAM | 4 GB | 16+ GB |
| Storage | 100 GB | 500+ GB |
| Network | 10 Mbps | 100 Mbps |

#### Operating System Setup

```bash
# Ubuntu 20.04 LTS
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python
sudo apt-get install python3.10 python3.10-venv python3-pip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Systemd Service

Create `/etc/systemd/system/qfzz.service`:

```ini
[Unit]
Description=QFZZ Radio Station
After=network.target

[Service]
Type=simple
User=qfzz
WorkingDirectory=/opt/qfzz
Environment="PATH=/opt/qfzz/venv/bin"
ExecStart=/opt/qfzz/venv/bin/python -m qfzz.server
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable qfzz
sudo systemctl start qfzz
sudo systemctl status qfzz
```

#### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/qfzz`:

```nginx
upstream qfzz_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name qfzz.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name qfzz.example.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/qfzz.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/qfzz.example.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Proxy settings
    location / {
        proxy_pass http://qfzz_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://qfzz_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/qfzz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Production Best Practices

### Configuration Management

!!! tip "Production Configuration"
    Always use environment variables and secrets management for production credentials.

```python
import os
from qfzz.core.config import StationConfig

# Load from environment
config = StationConfig(
    station_id=os.getenv("QFZZ_STATION_ID"),
    station_name=os.getenv("QFZZ_STATION_NAME", "Production Station"),
    enable_blockchain=os.getenv("QFZZ_ENABLE_BLOCKCHAIN", "true").lower() == "true",
    enable_edge_optimization=os.getenv("QFZZ_ENABLE_EDGE_OPT", "true").lower() == "true",
    trust_threshold=float(os.getenv("QFZZ_TRUST_THRESHOLD", "0.7")),
    cache_size_mb=int(os.getenv("QFZZ_CACHE_SIZE_MB", "1000"))
)
```

### Error Handling

```python
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def error_handling(operation_name):
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {str(e)}", exc_info=True)
        # Send alert to monitoring system
        send_alert(f"{operation_name} failed: {str(e)}")
        raise

# Usage
with error_handling("playlist_generation"):
    playlist = station.generate_playlist("user_id")
```

### Database Connection Pooling

```python
from contextlib import closing
import psycopg2.pool

# Create connection pool
conn_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    database="qfzz",
    user="qfzz_user",
    password="secure_password"
)

def get_db_connection():
    return conn_pool.getconn()

def release_db_connection(conn):
    conn_pool.putconn(conn)
```

### Rate Limiting

```python
from ratelimit import limits, sleep_and_retry
import time

CALLS_PER_MINUTE = 100

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
def api_endpoint(request):
    return process_request(request)
```

### Caching Strategy

```python
import redis
from functools import wraps
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cached(ttl_seconds=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

@cached(ttl_seconds=3600)
def get_playlist(user_id):
    return station.generate_playlist(user_id)
```

## Monitoring & Logging

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metrics
playlist_requests = Counter(
    'playlist_requests_total',
    'Total playlist requests'
)

playlist_latency = Histogram(
    'playlist_latency_seconds',
    'Playlist generation latency'
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# Usage
with playlist_latency.time():
    playlist = station.generate_playlist("user_id")
    playlist_requests.inc()

# Start metrics server
start_http_server(8001)
```

### ELK Stack Integration

```python
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log events
logger.info("playlist_generated", extra={
    "user_id": "user_123",
    "playlist_size": 20,
    "generation_time_ms": 245
})
```

### Application Performance Monitoring (APM)

```python
from elastic_apm import Client

apm_client = Client({
    'SERVICE_NAME': 'qfzz-station',
    'SERVER_URL': 'https://apm.example.com',
    'ENVIRONMENT': 'production'
})

# Automatic instrumentation of requests, database queries, etc.
```

## Scaling

### Horizontal Scaling

```bash
# Kubernetes horizontal scaling
kubectl autoscale deployment qfzz-station \
  --min=3 \
  --max=10 \
  --cpu-percent=70 \
  -n qfzz-prod

# Docker Swarm scaling
docker service scale qfzz=5
```

### Load Balancing

```python
# Round-robin load balancing
from itertools import cycle

servers = ['10.0.0.1:8000', '10.0.0.2:8000', '10.0.0.3:8000']
server_pool = cycle(servers)

def get_next_server():
    return next(server_pool)
```

### Database Scaling

```python
# Read replicas for database
# Primary: write operations
# Replicas: read operations

def get_db_connection(operation_type):
    if operation_type == 'write':
        return get_primary_connection()
    else:
        return get_replica_connection()
```

## Security Hardening

### TLS/SSL Configuration

```python
import ssl

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(
    certfile='/etc/ssl/certs/qfzz.crt',
    keyfile='/etc/ssl/private/qfzz.key'
)
ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20')
```

### API Authentication

```python
from functools import wraps
import jwt

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Missing API key'}, 401
        
        try:
            payload = jwt.decode(token, 'secret-key', algorithms=['HS256'])
            request.user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return {'error': 'Invalid API key'}, 401
        
        return f(*args, **kwargs)
    return decorated_function

@require_api_key
def protected_endpoint():
    return {'message': 'Success'}
```

### Input Validation

```python
from pydantic import BaseModel, validator

class PlaylistRequest(BaseModel):
    user_id: str
    limit: int
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Invalid user_id')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Limit must be between 1 and 1000')
        return v
```

### SQL Injection Prevention

```python
# Use parameterized queries
cursor.execute(
    "SELECT * FROM stations WHERE station_id = %s",
    (station_id,)
)

# Never use string concatenation
# Bad: cursor.execute(f"SELECT * FROM stations WHERE id = {station_id}")
# Good: cursor.execute("SELECT * FROM stations WHERE id = %s", (station_id,))
```

---

## Next Steps

1. **[Configuration Guide](configuration.md)** - Configure your deployment
2. **[Monitoring Guide](../monitoring.md)** - Set up monitoring
3. **[Security Guide](../security.md)** - Additional security hardening

## Support

For deployment issues:

1. Check relevant platform documentation
2. Review error logs
3. Ask in GitHub Discussions
4. Open a GitHub Issue
