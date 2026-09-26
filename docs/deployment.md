# Deployment

This guide covers building QFZZ documentation, optional local Firebase Hosting,
and the tip GitHub Actions workflow for Cloudflare Pages.

## Firebase Hosting Setup (manual)

Tip still ships `firebase.json` / `.firebaserc` for optional local hosting deploys.
There is **no** tip GitHub Actions workflow that deploys docs to Firebase.

### Prerequisites

- Firebase CLI installed
- Firebase project created
- Access to the `qfzz-radio` Firebase project (or your own)

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
- Set up automatic builds: No (tip CI/CD uses Cloudflare Pages — see below)

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

## GitHub Actions CI/CD (Cloudflare Pages)

### Required GitHub Secrets

Tip's docs deploy workflow expects:

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`

### Workflow Configuration

The workflow on tip is `.github/workflows/deploy-cloudflare-pages.yml`
(not a phantom `deploy-docs.yml` / Firebase Action):

```yaml
name: Deploy Docs to Cloudflare Pages

on:
  workflow_dispatch:

jobs:
  deploy:
    uses: fuzzywigg/project-template/.github/workflows/reusable-pages-static.yml@main
    with:
      project_name: qfzz-pappas-work
      output_dir: 'site'
      build_command: 'python -m pip install --upgrade pip && python -m pip install mkdocs-material "mkdocstrings[python]" && mkdocs build --site-dir site'
      production_branch: 'main'
    secrets:
      CLOUDFLARE_API_TOKEN:  ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

### Trigger Deployment

On tip this workflow is **manual** (`workflow_dispatch` only — no push-to-`main` auto-deploy):

1. GitHub → Actions → **Deploy Docs to Cloudflare Pages**
2. Run workflow

For broader Cloudflare DNS / Pages context, see [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md).

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

Create `config.yaml` with keys that match live `qfzz.core.config.StationConfig`
(required `station_id`; no `name` / `edge_mode` / `enable_6g` / `blockchain_enabled`):

```yaml
station:
  station_id: "qfzz"
  station_name: "My QFZZ Station"
  enable_blockchain: true
  enable_edge_optimization: true
```

Load in code:
```python
import yaml
from qfzz import QFZZStation, StationConfig

with open('config.yaml') as f:
    config_data = yaml.safe_load(f)

# Kwargs match live StationConfig (see docs/api/core.md)
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
    """Check station health via live get_station_stats() (no get_status() on tip)"""
    stats = station.get_station_stats()

    checks = {
        'running': stats['running'],
        'blockchain': stats['blockchain_enabled'],
        'edge': stats['edge_optimization_enabled'],
    }

    return all(checks.values())

if health_check(station):
    print("Station healthy")
else:
    print("Station unhealthy")
```

## Scaling

### Horizontal Scaling

Deploy multiple edge nodes:

```python
# Node 1 — station_id required on tip
station1 = QFZZStation(StationConfig(station_id="node-1", station_name="Node 1"))

# Node 2
station2 = QFZZStation(StationConfig(station_id="node-2", station_name="Node 2"))

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
- [ ] Firebase credentials secured (only if using manual Firebase Hosting)
- [ ] Cloudflare Pages secrets set (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`) when using tip Actions
- [ ] CI/CD pipeline tested (`workflow_dispatch` on `deploy-cloudflare-pages.yml`)

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Firebase Hosting](https://firebase.google.com/docs/hosting) (manual optional path on tip)
- [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md) (tip Pages / DNS context)
- Tip workflow: [`.github/workflows/deploy-cloudflare-pages.yml`](../.github/workflows/deploy-cloudflare-pages.yml)
- [GitHub Actions](https://docs.github.com/en/actions)
- [QFZZ Repository](https://github.com/fuzzywigg/QFZZ)
