# Getting Started

This guide will help you get started with QFZZ, from installation to running your first AI radio station.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

## Installation

### Clone the Repository

```bash
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ
```

### Install the Package

Install QFZZ in editable mode for development:

```bash
pip install -e .
```

Or install from PyPI (when available):

```bash
pip install qfzz
```

### Install Development Dependencies

If you want to contribute or build documentation:

```bash
pip install -r requirements-dev.txt
```

## First Steps

### 1. Basic Radio Station

Create your first QFZZ radio station:

```python
from qfzz import QFZZStation, StationConfig

# Create configuration
config = StationConfig(
    station_name="My First Station",
    edge_mode=True,
    blockchain_enabled=True
)

# Initialize and start station
station = QFZZStation(config)
station.initialize()
station.start()

# Get station status
status = station.get_status()
print(f"Station {status['name']} is running: {status['running']}")

# Stop station
station.stop()
```

Run the example:

```bash
python examples/basic_station.py
```

### 2. Personalized DJ Interaction

Create an AI DJ that learns your preferences:

```python
from qfzz import PersonalizedDJ

# Create DJ
dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Greet user
greeting = dj.greet_user("user_001", "Alex")
print(greeting)

# Interact with DJ
response = dj.interact("user_001", "Can you recommend some music?")
print(response)

# Update preferences
dj.update_preferences("user_001", ["jazz", "electronic", "ambient"])

# Ask for music again
response = dj.interact("user_001", "Play something for me")
print(response)

# Check trust score
trust_score = dj.get_trust_score("user_001")
print(f"Trust score: {trust_score:.2f}")
```

Run the example:

```bash
python examples/personalized_dj_demo.py
```

### 3. Dataset Management

Register and manage opensource datasets:

```python
from qfzz import DatasetManager, Dataset, DatasetLicense

# Create dataset manager
manager = DatasetManager(opensource_only=True, min_quality=0.7)

# Register a dataset
dataset = Dataset(
    id="ds_001",
    name="OpenMusic Dataset",
    description="High-quality open source music samples",
    license=DatasetLicense.CC_BY,
    source_url="https://example.com/openmusic",
    quality_score=0.9,
    category="music",
    size_mb=150.0
)

# Register and verify
success = manager.register_dataset(dataset)
if success:
    manager.verify_dataset_blockchain(dataset.id)
    manager.rate_dataset(dataset.id, 0.85)

# Get high quality datasets
high_quality = manager.get_high_quality_datasets()
print(f"Found {len(high_quality)} high quality datasets")

# Get edge-optimized datasets
edge_datasets = manager.get_edge_optimized_datasets(max_size_mb=100)
print(f"Found {len(edge_datasets)} edge-optimized datasets")
```

Run the example:

```bash
python examples/dataset_management.py
```

### 4. Blockchain Trust Network

Use blockchain for trust and verification:

```python
from qfzz import BlockchainTrustNetwork, TrustRecord

# Create blockchain
blockchain = BlockchainTrustNetwork()

# Add trust records
record = TrustRecord("user_001", "interaction", "dj", 0.05)
blockchain.add_trust_record(record)

# Mine a block
block = blockchain.mine_block()
print(f"Mined block #{block.index}")

# Verify chain integrity
is_valid = blockchain.verify_chain()
print(f"Blockchain valid: {is_valid}")

# Get trust score
score = blockchain.get_trust_score("user_001")
print(f"Trust score: {score:.2f}")
```

Run the example:

```bash
python examples/blockchain_demo.py
```

### 5. Edge Device Optimization

Optimize for edge devices:

```python
from qfzz import EdgeOptimizer, EdgeDeviceConfig

# Configure edge device
config = EdgeDeviceConfig(
    device_id="edge_001",
    device_type="smartphone",
    max_memory_mb=512,
    max_model_size_mb=100,
    enable_6g=True,
    network_bandwidth_mbps=1000
)

# Create optimizer
optimizer = EdgeOptimizer(config)

# Optimize model
model_opt = optimizer.optimize_model(250.0)
print(f"Model optimization: {model_opt}")

# Optimize streaming
streaming_config = optimizer.optimize_streaming(320)
print(f"Streaming config: {streaming_config}")

# Use local caching
optimizer.add_to_cache("track_001", {"title": "Test Track"}, 5.0)
cached = optimizer.get_from_cache("track_001")
print(f"Cached data: {cached}")
```

Run the example:

```bash
python examples/edge_optimization.py
```

## Run All Demos

To run all demonstration scripts at once:

```bash
python main.py
```

## Testing Your Installation

Run the test suite to ensure everything is working:

```bash
pytest tests/
```

## Configuration Options

### Station Configuration

The `StationConfig` class provides various configuration options:

```python
StationConfig(
    station_name="QFZZ",                    # Station name
    station_tagline="The Pulse...",         # Tagline
    edge_mode=True,                         # Edge device optimization
    max_model_size_mb=500,                  # Max model size
    enable_6g=False,                        # 6G network support
    network_protocol="http",                # Network protocol
    blockchain_enabled=True,                # Enable blockchain
    chain_type="trust_network",             # Blockchain type
    opensource_datasets_only=True,          # Only opensource datasets
    min_dataset_quality_score=0.7,          # Min quality score
    enable_personalization=True,            # Enable DJ personalization
    community_trust_threshold=0.8           # Trust threshold
)
```

### Edge Device Configuration

The `EdgeDeviceConfig` class configures edge deployment:

```python
EdgeDeviceConfig(
    device_id="edge_001",                   # Device identifier
    device_type="smartphone",               # Device type
    max_memory_mb=512,                      # Max memory
    max_model_size_mb=100,                  # Max model size
    enable_6g=False,                        # 6G support
    network_bandwidth_mbps=100,             # Bandwidth
    storage_available_gb=1.0                # Storage
)
```

## Next Steps

Now that you have QFZZ installed and running, explore:

- 🏗️ [Architecture](architecture.md) - Learn about the system design
- 📚 [API Reference](api/core.md) - Detailed API documentation
- 🎓 [Guides](guides/quantum-security.md) - Advanced usage guides
- 🚀 [Deployment](deployment.md) - Deploy to production

## Troubleshooting

### Import Errors

If you encounter import errors, make sure you installed the package:

```bash
pip install -e .
```

### Python Version

Ensure you're using Python 3.8 or higher:

```bash
python --version
```

### Dependencies

Install all development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Getting Help

- 📖 Check the [documentation](index.md)
- 🐛 [Report issues](https://github.com/fuzzywigg/QFZZ/issues)
- 💬 Start a [discussion](https://github.com/fuzzywigg/QFZZ/discussions)
