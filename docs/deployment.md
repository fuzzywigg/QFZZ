# Deployment

This guide covers deploying QFZZ documentation to Firebase and setting up CI/CD.

## Firebase Hosting Setup

### Prerequisites

- Firebase CLI installed
- Firebase project created
- GitHub repository access

### 1. Install Firebase CLI

```bash
npm install -g firebase-tools
```

### 2. Login to Firebase

```bash
firebase login
```

### 3. Initialize Firebase in Your Project

```bash
cd QFZZ
firebase init hosting
```

Select:
- Use existing project: `qfzz-radio`
- Public directory: `site`
- Configure as single-page app: No
- Set up automatic builds: No (we'll use GitHub Actions)

### 4. Build Documentation

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Build docs
mkdocs build

# Test locally
mkdocs serve
```

Visit `http://localhost:8000` to preview.

### 5. Deploy to Firebase

```bash
firebase deploy --only hosting
```

Your documentation will be available at: `https://qfzz-radio.web.app`

## GitHub Actions CI/CD

### Setup Firebase Service Account

1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Generate new private key
4. Save as JSON

### Add to GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add secret: `FIREBASE_SERVICE_ACCOUNT`
4. Paste the JSON content

### Workflow Configuration

The workflow is already configured in `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'qfzz/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install mkdocs-material mkdocstrings[python] pymdown-extensions
      
      - name: Build documentation
        run: mkdocs build
      
      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          channelId: live
          projectId: qfzz-radio
```

### Trigger Deployment

Push to main branch to automatically deploy:

```bash
git add .
git commit -m "Update documentation"
git push origin main
```

## Production Deployment

### Package Installation

For users to install QFZZ:

```bash
pip install qfzz
```

Or from source:

```bash
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ
pip install -e .
```

### Edge Device Deployment

#### Raspberry Pi

```bash
# Install Python
sudo apt-get update
sudo apt-get install python3 python3-pip

# Clone and install
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ
pip3 install -e .

# Run
python3 main.py
```

#### Android (Termux)

```bash
# Install Termux from F-Droid
# In Termux:
pkg install python
pip install qfzz

# Run
python main.py
```

#### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install -e .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t qfzz .
docker run qfzz
```

## Environment Configuration

### Configuration File

Create `config.yaml`:

```yaml
station:
  name: "My QFZZ Station"
  edge_mode: true
  enable_6g: false
  blockchain_enabled: true

datasets:
  opensource_only: true
  min_quality: 0.7

edge:
  device_type: "smartphone"
  max_memory_mb: 512
  max_model_size_mb: 100
```

Load in code:
```python
import yaml
from qfzz import QFZZStation, StationConfig

with open('config.yaml') as f:
    config_data = yaml.safe_load(f)
    
config = StationConfig(**config_data['station'])
station = QFZZStation(config)
```

### Environment Variables

```bash
export QFZZ_EDGE_MODE=true
export QFZZ_BLOCKCHAIN_ENABLED=true
export QFZZ_MIN_QUALITY=0.7
```

## Monitoring

### Logging

Configure logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qfzz.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

```python
def health_check(station):
    """Check station health"""
    status = station.get_status()
    
    checks = {
        'running': status['running'],
        'blockchain': status['blockchain_enabled'],
        'edge_mode': status['edge_mode']
    }
    
    return all(checks.values())

if health_check(station):
    print("✅ Station healthy")
else:
    print("❌ Station unhealthy")
```

## Scaling

### Horizontal Scaling

Deploy multiple edge nodes:

```python
# Node 1
station1 = QFZZStation(StationConfig(station_name="Node 1"))

# Node 2
station2 = QFZZStation(StationConfig(station_name="Node 2"))

# Federation (future feature)
# station1.federate_with(station2)
```

### Load Balancing

For API services (future):

```nginx
upstream qfzz_nodes {
    server node1:8000;
    server node2:8000;
    server node3:8000;
}

server {
    location / {
        proxy_pass http://qfzz_nodes;
    }
}
```

## Maintenance

### Backup

Backup blockchain data:
```bash
# Export blockchain
python -c "from qfzz import BlockchainTrustNetwork; \
           import pickle; \
           bc = BlockchainTrustNetwork(); \
           pickle.dump(bc.chain, open('blockchain_backup.pkl', 'wb'))"
```

### Updates

Update QFZZ:
```bash
pip install --upgrade qfzz
```

Or from source:
```bash
git pull origin main
pip install -e .
```

## Troubleshooting

### Documentation Build Fails

```bash
# Clear MkDocs cache
rm -rf site/

# Reinstall dependencies
pip install -r requirements-dev.txt

# Rebuild
mkdocs build
```

### Firebase Deploy Fails

Check:
- Firebase CLI version: `firebase --version`
- Login status: `firebase login:list`
- Project ID: `firebase projects:list`

Re-authenticate:
```bash
firebase logout
firebase login
```

### Import Errors

```bash
# Reinstall package
pip uninstall qfzz
pip install -e .

# Check installation
python -c "import qfzz; print(qfzz.__version__)"
```

## Production Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] Documentation built successfully
- [ ] Environment variables configured
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Security review completed
- [ ] Performance tested
- [ ] Firebase credentials secured
- [ ] CI/CD pipeline tested

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Firebase Hosting](https://firebase.google.com/docs/hosting)
- [GitHub Actions](https://docs.github.com/en/actions)
- [QFZZ Repository](https://github.com/fuzzywigg/QFZZ)
