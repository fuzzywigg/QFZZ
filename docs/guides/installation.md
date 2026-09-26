# QFZZ Installation Guide

Complete guide to installing QFZZ on any platform, from pip to Docker, with troubleshooting for every scenario.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start Installation](#quick-start-installation)
- [Detailed Installation Methods](#detailed-installation-methods)
- [Virtual Environments](#virtual-environments)
- [Dependency Management](#dependency-management)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Docker Installation](#docker-installation)
- [Verification Steps](#verification-steps)
- [Troubleshooting](#troubleshooting)
- [Uninstalling QFZZ](#uninstalling-qfzz)

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|------------|
| **Python Version** | 3.8 or higher |
| **RAM** | 512 MB minimum |
| **Disk Space** | 100 MB for package + data |
| **Package Manager** | pip 20.0+ or conda 4.8+ |

### Recommended Requirements

| Component | Recommendation |
|-----------|--------------|
| **Python Version** | 3.10 or higher |
| **RAM** | 2 GB or more |
| **Disk Space** | 500 MB+ for optimal caching |
| **Network** | Broadband for streaming features |

### Supported Platforms

- ✅ **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 7+, Fedora 30+
- ✅ **macOS**: 10.14+, both Intel and Apple Silicon
- ✅ **Windows**: Windows 10/11, both 32-bit and 64-bit
- ✅ **Docker**: Any system with Docker Engine 20.10+

### Optional Requirements

- **Firebase Deployment**: Active Firebase project and credentials
- **Cloud Deployment**: AWS/GCP/Azure account (for cloud deployment)
- **Development**: Git 2.0+ for source installation

## Quick Start Installation

### Using pip (Easiest)

```bash
# Install latest stable version
pip install qfzz

# Verify installation
python -c "import qfzz; print(qfzz.__version__)"
```

**Installation Time**: ~2-3 minutes (depending on internet speed)

### Using conda

```bash
# Install from conda-forge
conda install -c conda-forge qfzz

# Verify installation
python -c "import qfzz; print(qfzz.__version__)"
```

### From Source (Development)

```bash
# Clone repository
git clone https://github.com/yourusername/qfzz.git
cd qfzz

# Install in development mode
pip install -e .

# Verify installation
python -c "import qfzz; print(qfzz.__version__)"
```

!!! success "Installation Complete!"
    Your QFZZ installation is ready. Move on to the [Configuration Guide](configuration.md) to set up your station.

## Detailed Installation Methods

### Method 1: PyPI (pip) Installation

This is the recommended method for most users.

```bash
# Step 1: Upgrade pip (recommended)
pip install --upgrade pip

# Step 2: Install QFZZ
pip install qfzz

# Step 3: (Optional) Install optional dependencies
pip install qfzz[firebase,dev]
```

#### Installation Options

```bash
# Core installation (minimal)
pip install qfzz

# With Firebase support
pip install qfzz[firebase]

# With development tools (for contributing)
pip install qfzz[dev]

# With all optional dependencies
pip install qfzz[all]
```

#### Specifying Version

```bash
# Install specific version
pip install qfzz==1.0.0

# Install latest from a specific major version
pip install qfzz==1.*

# Install pre-release versions
pip install --pre qfzz
```

### Method 2: Conda Installation

```bash
# Step 1: Update conda (optional but recommended)
conda update conda

# Step 2: Install QFZZ from conda-forge
conda install -c conda-forge qfzz

# Step 3: (Optional) Create environment with specific Python version
conda create -n qfzz-env python=3.10 qfzz
conda activate qfzz-env
```

#### Conda-Forge Channel

```bash
# Add conda-forge as default channel
conda config --add channels conda-forge

# Install QFZZ without specifying channel each time
conda install qfzz
```

### Method 3: Installation from Source

Recommended for developers and contributors.

```bash
# Step 1: Clone repository
git clone https://github.com/yourusername/qfzz.git
cd qfzz

# Step 2: Install in editable mode
pip install -e .

# Step 3: Install development dependencies
pip install -e ".[dev,firebase]"

# Step 4: Verify
python -m pytest tests/ -v
```

#### Source Installation Options

```bash
# Install for local development (editable)
pip install -e .

# Install with all development tools
pip install -e ".[dev]"

# Install with Firebase support
pip install -e ".[firebase]"

# Install all optional dependencies
pip install -e ".[all]"

# Install specific versions for development
pip install -e ".[dev,firebase]"
```

### Method 4: Using Build Tools

```bash
# Step 1: Clone and navigate
git clone https://github.com/yourusername/qfzz.git
cd qfzz

# Step 2: Build distribution packages
python -m build

# Step 3: Install from wheel
pip install dist/qfzz-*.whl
```

## Virtual Environments

### Using venv (Python Standard)

```bash
# Step 1: Create virtual environment
python -m venv qfzz-venv

# Step 2: Activate virtual environment

# On Linux/macOS:
source qfzz-venv/bin/activate

# On Windows:
qfzz-venv\Scripts\activate

# Step 3: Install QFZZ
pip install qfzz

# Step 4: Deactivate when done
deactivate
```

#### Creating for Specific Python Version

```bash
# Create with Python 3.10
python3.10 -m venv qfzz-venv-310

# Create with specific paths
python -m venv /path/to/qfzz-venv
```

### Using virtualenv

```bash
# Step 1: Install virtualenv (if not already installed)
pip install virtualenv

# Step 2: Create virtual environment
virtualenv qfzz-venv

# Step 3: Activate
# On Linux/macOS:
source qfzz-venv/bin/activate

# On Windows:
qfzz-venv\Scripts\activate

# Step 4: Install QFZZ
pip install qfzz
```

### Using Conda Environments

```bash
# Step 1: Create conda environment with Python 3.10
conda create -n qfzz python=3.10

# Step 2: Activate environment
conda activate qfzz

# Step 3: Install QFZZ
pip install qfzz

# Step 4: Verify
python -c "import qfzz; print(qfzz.__version__)"

# Step 5: Deactivate when done
conda deactivate
```

#### Multiple Environments

```bash
# Create different environments for different versions
conda create -n qfzz-latest python=3.11 qfzz
conda create -n qfzz-stable python=3.10 qfzz==1.0.0

# List all environments
conda env list

# Switch between environments
conda activate qfzz-latest
conda activate qfzz-stable
```

### Using Poetry

```bash
# Step 1: Create project with QFZZ
poetry new my-qfzz-project
cd my-qfzz-project

# Step 2: Add QFZZ dependency
poetry add qfzz

# Step 3: Add development dependencies
poetry add --group dev pytest pytest-cov

# Step 4: Enter virtual environment
poetry shell

# Step 5: Run commands
poetry run python -c "import qfzz"
```

!!! note "Virtual Environment Best Practices"
    Always use a virtual environment when developing or deploying QFZZ. This prevents conflicts with system Python packages and ensures reproducible installations.

## Dependency Management

### Core Dependencies

QFZZ has minimal core dependencies:

```
- Python >= 3.8
- dataclasses-json >= 0.5.0
- numpy >= 1.19.0
- Pillow >= 8.0.0
```

### Optional Dependencies

| Feature | Package | Version |
|---------|---------|---------|
| Firebase | `firebase-admin` | >=5.0.0 |
| AWS | `boto3` | >=1.20.0 |
| Google Cloud | `google-cloud-storage` | >=2.0.0 |
| Azure | `azure-storage-blob` | >=12.0.0 |
| Development | `pytest`, `black`, `flake8` | Latest |

### Installing Specific Dependencies

```bash
# Firebase support only
pip install qfzz[firebase]

# AWS support only
pip install qfzz[aws]

# All cloud providers
pip install qfzz[cloud]

# Development tools
pip install qfzz[dev]

# Documentation building
pip install qfzz[docs]
```

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Show installed packages
pip list

# Show dependency tree
pip install pipdeptree
pipdeptree -p qfzz

# Check for conflicts
pip check

# Try installing with --no-deps to debug
pip install qfzz --no-deps
```

### Using Requirements Files

```bash
# Create requirements file
pip freeze > requirements.txt

# Install from requirements file
pip install -r requirements.txt

# Production requirements
echo "qfzz==1.0.0" > requirements-prod.txt
pip install -r requirements-prod.txt
```

## Platform-Specific Instructions

### Linux Installation

#### Ubuntu/Debian

```bash
# Update package manager
sudo apt-get update

# Install Python and pip
sudo apt-get install python3.10 python3.10-venv python3-pip

# Create virtual environment
python3.10 -m venv qfzz-venv

# Activate virtual environment
source qfzz-venv/bin/activate

# Install QFZZ
pip install --upgrade pip
pip install qfzz

# Verify
python -c "import qfzz; print('QFZZ installed successfully!')"
```

#### CentOS/RHEL

```bash
# Install dependencies
sudo yum install python3.10 python3-pip

# Create virtual environment
python3.10 -m venv qfzz-venv

# Activate and install
source qfzz-venv/bin/activate
pip install --upgrade pip
pip install qfzz
```

#### Fedora

```bash
# Install Python
sudo dnf install python3.10 python3-pip

# Create and activate virtual environment
python3.10 -m venv qfzz-venv
source qfzz-venv/bin/activate

# Install QFZZ
pip install qfzz
```

### macOS Installation

#### Using Homebrew (Intel Mac)

```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Create virtual environment
python3.10 -m venv qfzz-venv

# Activate
source qfzz-venv/bin/activate

# Install QFZZ
pip install qfzz
```

#### Using Homebrew (Apple Silicon)

```bash
# Install Homebrew for Apple Silicon (automatically handles architecture)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python (automatically native for Apple Silicon)
brew install python@3.10

# Create and activate virtual environment
python3.10 -m venv qfzz-venv
source qfzz-venv/bin/activate

# Install QFZZ
pip install qfzz
```

#### Using Conda (Recommended for Apple Silicon)

```bash
# Install Miniconda/Anaconda (supports both Intel and Apple Silicon)
# Download from https://www.anaconda.com/download/

# Create environment
conda create -n qfzz python=3.10

# Activate
conda activate qfzz

# Install QFZZ
pip install qfzz
```

### Windows Installation

#### PowerShell Method

```powershell
# Step 1: Install Python from microsoft.com/python
# Or use Scoop:
scoop install python

# Step 2: Create virtual environment
python -m venv qfzz-venv

# Step 3: Activate virtual environment
qfzz-venv\Scripts\Activate.ps1

# Step 4: Install QFZZ
pip install --upgrade pip
pip install qfzz

# Step 5: Verify
python -c "import qfzz; print('QFZZ installed successfully!')"
```

#### Command Prompt Method

```cmd
# Step 1: Create virtual environment
python -m venv qfzz-venv

# Step 2: Activate (Command Prompt)
qfzz-venv\Scripts\activate.bat

# Step 3: Install
pip install --upgrade pip
pip install qfzz

# Step 4: Verify
python -c "import qfzz; print('QFZZ installed successfully!')"
```

#### Using Conda on Windows

```powershell
# Install Anaconda/Miniconda from https://www.anaconda.com/download/

# Open Anaconda Prompt
# Create environment
conda create -n qfzz python=3.10

# Activate
conda activate qfzz

# Install QFZZ
pip install qfzz
```

!!! tip "Windows Path Issues"
    If you encounter path issues, ensure Python is in your PATH by:
    1. Opening Settings → System → About
    2. Clicking "Advanced system settings"
    3. Clicking "Environment Variables"
    4. Adding Python installation directory to PATH

## Docker Installation

### Quick Docker Setup

```bash
# Pull official QFZZ Docker image
docker pull qfzz/qfzz:latest

# Run QFZZ container
docker run -it qfzz/qfzz:latest python -c "import qfzz; print(qfzz.__version__)"
```

### Docker File

Create a `Dockerfile` for your QFZZ application:

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (if using requirements.txt)
COPY requirements.txt .

# Install QFZZ and dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (if running web server)
EXPOSE 8000

# Default command
CMD ["python", "main.py"]
```

### Docker Compose

Create `docker-compose.yml` for local development:

```yaml
version: '3.8'

services:
  qfzz-app:
    build: .
    container_name: qfzz-station
    environment:
      - QFZZ_STATION_ID=docker_station
      - QFZZ_STATION_NAME=Docker QFZZ Station
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    ports:
      - "8000:8000"
    command: python app.py

  # Optional: Add Redis for caching
  redis:
    image: redis:7-alpine
    container_name: qfzz-redis
    ports:
      - "6379:6379"
```

Run with Docker Compose:

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f qfzz-app

# Stop containers
docker-compose down
```

### Building Custom Docker Image

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app
RUN pip install qfzz[firebase,aws]
COPY . .
CMD ["python", "run_server.py"]
EOF

# Build image
docker build -t my-qfzz:latest .

# Run container
docker run -it my-qfzz:latest
```

### Kubernetes Deployment

Create `qfzz-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qfzz-station
  labels:
    app: qfzz
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
        image: qfzz/qfzz:latest
        ports:
        - containerPort: 8000
        env:
        - name: QFZZ_STATION_NAME
          value: "Kubernetes Station"
        - name: QFZZ_ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

Deploy to Kubernetes:

```bash
# Apply deployment
kubectl apply -f qfzz-deployment.yaml

# Verify deployment
kubectl get deployments
kubectl get pods
```

## Verification Steps

### Step 1: Verify Installation

```python
# Create test_installation.py
import qfzz

print(f"QFZZ Version: {qfzz.__version__}")
print(f"QFZZ Location: {qfzz.__file__}")
print(f"Installation successful!")
```

Run verification:

```bash
python test_installation.py
```

### Step 2: Test Core Import

```python
# test_core_import.py
from qfzz import QFZZStation, StationConfig
from qfzz.core.config import StationConfig
from qfzz.edge.config import EdgeDeviceConfig, DeviceType
from qfzz.datasets import DatasetManager
from qfzz.dj import PersonalizedDJ
from qfzz.blockchain import BlockchainTrustNetwork

print("✓ All core modules imported successfully!")
```

### Step 3: Test Station Creation

```python
# test_station_creation.py
from qfzz import QFZZStation, StationConfig

# Create configuration
config = StationConfig(
    station_id="test_station",
    station_name="Test Station"
)

# Create station
station = QFZZStation(config)
print(f"✓ Station created: {station.config.station_name}")

# Start station
station.start()
print("✓ Station started successfully!")

# Get stats
stats = station.get_station_stats()
print(f"✓ Station stats retrieved: {stats['station_name']}")

# Stop station
station.stop()
print("✓ Station stopped successfully!")
```

Run test:

```bash
python test_station_creation.py
```

### Step 4: Complete Verification Script

```python
# verify_installation.py
import sys

def test_import():
    """Test basic imports."""
    try:
        import qfzz
        from qfzz import QFZZStation, StationConfig
        print("✓ Import test passed")
        return True
    except ImportError as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_configuration():
    """Test configuration creation."""
    try:
        from qfzz import StationConfig
        config = StationConfig(
            station_id="test",
            station_name="Test Station"
        )
        assert config.validate() is None
        print("✓ Configuration test passed")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_station():
    """Test station creation and basic operations."""
    try:
        from qfzz import QFZZStation, StationConfig

        config = StationConfig(
            station_id="test",
            station_name="Test Station"
        )
        station = QFZZStation(config)
        station.start()
        assert station.is_running()
        station.stop()
        assert not station.is_running()
        print("✓ Station test passed")
        return True
    except Exception as e:
        print(f"✗ Station test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🧪 QFZZ Installation Verification\n")

    tests = [
        test_import,
        test_configuration,
        test_station
    ]

    results = [test() for test in tests]

    print(f"\n{'='*40}")
    if all(results):
        print("✓ All verification tests passed!")
        print("🎉 QFZZ is properly installed!")
        return 0
    else:
        print("✗ Some verification tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Run complete verification:

```bash
python verify_installation.py
```

## Troubleshooting

### Common Installation Issues

#### Issue: "pip: command not found"

**Solution**: Python or pip is not installed or not in PATH.

```bash
# On macOS
brew install python@3.10

# On Ubuntu/Debian
sudo apt-get install python3-pip

# On Windows, download from https://www.python.org/downloads/
# Or use: scoop install python

# Verify pip is installed
pip --version
```

#### Issue: "ModuleNotFoundError: No module named 'qfzz'"

**Solution**: QFZZ not installed or using wrong Python interpreter.

```bash
# Verify QFZZ is installed
pip list | grep qfzz

# Reinstall QFZZ
pip uninstall qfzz
pip install qfzz

# Check Python version
python --version  # Should be 3.8+

# Verify installation location
python -c "import qfzz; print(qfzz.__file__)"
```

#### Issue: "Permission denied" errors

**Solution**: Use virtual environment or user-level install.

```bash
# Option 1: Use virtual environment (recommended)
python -m venv qfzz-venv
source qfzz-venv/bin/activate
pip install qfzz

# Option 2: Install for user only
pip install --user qfzz

# Option 3: Use sudo (not recommended)
sudo pip install qfzz
```

#### Issue: "Requirement already satisfied" during installation

**Solution**: This is normal, but if you need to update:

```bash
# Upgrade existing installation
pip install --upgrade qfzz

# Force reinstall (if corrupted)
pip install --force-reinstall qfzz

# Install specific version
pip install qfzz==1.0.0 --force-reinstall
```

#### Issue: Platform-specific compilation errors

**Solution**: Install build tools.

```bash
# On Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# On macOS
xcode-select --install

# On Windows
# Download Visual C++ Build Tools from:
# https://visualstudio.microsoft.com/downloads/
```

#### Issue: Virtual environment not activating (Windows)

**Solution**: PowerShell execution policy.

```powershell
# Check policy
Get-ExecutionPolicy

# Set to allow local scripts (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Debugging Installation Issues

#### Check Installation Details

```bash
# Show all QFZZ-related packages
pip list | grep -i qfzz

# Show detailed installation info
pip show qfzz

# Show dependency tree
pip install pipdeptree
pipdeptree -p qfzz

# Check for conflicts
pip check
```

#### Get Diagnostic Information

```python
# Create diagnostics.py
import sys
import platform
import importlib

def diagnose():
    print("=== System Information ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Python Executable: {sys.executable}")

    print("\n=== Installed Packages ===")
    try:
        import qfzz
        print(f"QFZZ: {qfzz.__version__}")
        print(f"Location: {qfzz.__file__}")
    except ImportError as e:
        print(f"QFZZ: NOT INSTALLED ({e})")

    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"  {path}")

if __name__ == "__main__":
    diagnose()
```

Run diagnostics:

```bash
python diagnostics.py
```

## Uninstalling QFZZ

### Remove Installation

```bash
# Uninstall QFZZ
pip uninstall qfzz

# Uninstall QFZZ and dependencies
pip uninstall qfzz -y

# Remove virtual environment
rm -rf qfzz-venv  # Linux/macOS
rmdir /s qfzz-venv  # Windows
```

### Clean Up Installation Cache

```bash
# Clear pip cache
pip cache purge

# Remove build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
```

### Complete Uninstall

```bash
# Remove QFZZ and all traces
pip uninstall qfzz -y

# Remove config files (if saved)
rm -rf ~/.qfzz/
rm -rf ~/.config/qfzz/

# Remove cache
rm -rf ~/.cache/pip/
```

---

## Next Steps

Now that QFZZ is installed, proceed to:

1. **[Configuration Guide](configuration.md)** - Set up your station configuration
2. **[Getting Started](../getting-started.md)** - Create your first station
3. **[Deployment Guide](deployment.md)** - Deploy to production

## Support

If you encounter issues not covered here:

1. **Check [GitHub Issues](https://github.com/yourusername/qfzz/issues)**
2. **Read the [FAQ](../faq.md)**
3. **Ask in [GitHub Discussions](https://github.com/yourusername/qfzz/discussions)**
4. **Join our [Discord Community](https://discord.gg/qfzz)**
