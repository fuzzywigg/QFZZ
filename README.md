# QFZZ: The Pulse of the Quantum Realm 🎵🤖

[![CI](https://github.com/fuzzywigg/QFZZ/actions/workflows/ci.yml/badge.svg)](https://github.com/fuzzywigg/QFZZ/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI Radio for the Individual** - A next-generation radio station powered by AI, running on edge devices, secured with blockchain, and built on open source datasets.

## 🌟 Vision

QFZZ is an AI radio station inspired by projects like Andon Labs Radio Eval, designed to create a personalized music experience where:

- **Individualized LLMs** run on edge devices for personalized DJ interactions
- **GNU/OPENSOURCE datasets** power high-quality music curation and conversation
- **6G-ready infrastructure** enables ultra-low latency streaming
- **Blockchain security** ensures trust and data authenticity
- **Community-driven** discovery of quality datasets and music
- **Personal DJ** that knows you and is part of your community of trust

## 🏗️ Architecture

### Core Components

1. **QFZZStation** - Main radio station orchestrator
   - Manages all station components
   - Configurable for edge deployment
   - Blockchain-enabled trust network
   - Dataset quality management

2. **PersonalizedDJ** - AI DJ that learns and adapts
   - Conversational interaction
   - Music curation based on preferences and mood
   - Community trust building
   - Edge device optimized

3. **DatasetManager** - GNU/OPENSOURCE dataset handling
   - Quality scoring and visibility
   - Blockchain verification
   - Community ratings
   - Edge device optimization

4. **BlockchainTrustNetwork** - Security and trust layer
   - Immutable trust records
   - Dataset verification
   - User identity security
   - Community trust scoring

5. **EdgeOptimizer** - Edge device deployment
   - Model size optimization
   - 6G network support
   - Bandwidth-aware streaming
   - Local caching

## 🚀 Quick Start

### Installation

#### Windows Users (PowerShell)

**📘 For a complete Windows guide with PowerShell commands, see [docs/QUICK_START_WINDOWS.md](docs/QUICK_START_WINDOWS.md)**

Quick start for Windows:
```powershell
# Clone and navigate
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ

# Set up Python backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# In a new PowerShell window, set up frontend
cd QFZZ\frontend
npm install

# Start backend (first window)
cd ..
python run_server.py

# Start frontend (second window)
cd frontend
npm run dev

# Open http://localhost:3000 in your browser
```

#### Linux/Mac Users

```bash
# Clone the repository
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ

# Install dependencies
pip install -r requirements.txt

# Run the demo
python main.py
```

### Basic Usage

#### Running the Full GUI Application

To run the complete QFZZ experience with the web GUI:

```bash
# Terminal 1: Start the backend server
python run_server.py

# Terminal 2: Start the frontend
cd frontend
npm run dev

# Open http://localhost:3000 in your browser
```

For Windows PowerShell instructions, see [docs/QUICK_START_WINDOWS.md](docs/QUICK_START_WINDOWS.md).

#### Using Python API

```python
from qfzz import QFZZStation, PersonalizedDJ
from qfzz.core import StationConfig

# Create and start a station
config = StationConfig(
    station_name="QFZZ",
    edge_mode=True,
    enable_6g=False,
    blockchain_enabled=True
)

station = QFZZStation(config)
station.initialize()
station.start()

# Create a personalized DJ
dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)

# Interact with the DJ
greeting = dj.greet_user("user_001", "Alex")
print(greeting)

response = dj.interact("user_001", "Can you recommend some music?")
print(response)
```

## 🔧 Configuration

QFZZ uses environment variables for configuration.

### Quick Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   - **`GEMINI_API_KEY`**: used by `run_server.py` and `qfzz/config/settings.py` for the local demo runners
   - **`GOOGLE_AI_API_KEY`**: used by `qfzz/core/llm_router.py` (and `qfzz/app_config.py`) for the multi-provider router
   - **Recommended**: Also add `GROQ_API_KEY` for free tier backup
   - **Optional**: Add other providers for maximum reliability

3. Get API Keys:
   - Google Gemini: https://makersuite.google.com/app/apikey
   - Groq (free): https://console.groq.com
   - Anthropic: https://console.anthropic.com
   - OpenAI: https://platform.openai.com/api-keys

### Local-Only Setup (No API Keys)

You can run QFZZ entirely locally with Ollama:

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull mistral:7b-instruct

# Run QFZZ (will automatically use local Ollama)
python main.py
```

No API keys needed! 🎉

### Configuration Options

See `.env.example` for all available configuration options.

## 💡 Key Features

### 🎧 Personalized DJ Experience
- AI-powered DJ that learns your music preferences
- Contextual responses based on mood and history
- Community connection features
- Trust-building over time

### 📊 Dataset Quality & Transparency
- Only GNU/OPENSOURCE licensed datasets
- Quality scoring (0.0 to 1.0)
- Community ratings and reviews
- Blockchain verification for authenticity

### 🔒 Blockchain Security
- Immutable trust records
- Dataset authenticity verification
- User identity security
- Community trust scoring

### 📱 Edge Device Ready
- Optimized for resource-constrained devices
- Model quantization and pruning
- Smart caching strategies
- 6G network optimization

### 🌐 6G Network Support
- High bandwidth, low latency streaming
- Adaptive quality based on network conditions
- Future-ready infrastructure
- Optimized buffer management

## 📖 Examples

### Dataset Management

```python
from qfzz.datasets import DatasetManager, Dataset, DatasetLicense

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

manager.register_dataset(dataset)
manager.verify_dataset_blockchain(dataset.id)

# Get high quality datasets
high_quality = manager.get_high_quality_datasets()

# Get edge-optimized datasets
edge_datasets = manager.get_edge_optimized_datasets(max_size_mb=100)
```

### Edge Device Optimization

```python
from qfzz.edge import EdgeOptimizer, EdgeDeviceConfig

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

# Optimize model for edge deployment
optimization = optimizer.optimize_model(250.0)

# Get streaming configuration
streaming = optimizer.optimize_streaming(320)
```

### Blockchain Trust Network

```python
from qfzz.blockchain import BlockchainTrustNetwork, TrustRecord

# Create blockchain
blockchain = BlockchainTrustNetwork()

# Add trust records
record = TrustRecord("user_001", "interaction", "dj", 0.05)
blockchain.add_trust_record(record)

# Mine a block
block = blockchain.mine_block()

# Verify chain integrity
is_valid = blockchain.verify_chain()

# Get trust score
score = blockchain.get_trust_score("user_001")
```

## 🛠️ Technology Stack

- **Python 3.10+** (`requires-python = ">=3.10"` in `pyproject.toml`) - Core implementation
- **Next.js 16** (`frontend/`) - Local web player UI
- **Dataclasses** - Data structure definitions
- **Logging** - Comprehensive logging
- **Hashlib** - Blockchain hashing
- **Type Hints** - Full type safety

## 🛠️ Development

### Setup

```bash
# Quick setup (recommended)
./scripts/setup-dev-environment.sh

# Or manual setup
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

### Code Quality

We use pre-commit hooks to maintain code quality:
- **detect-secrets**: Prevents committing API keys
- **black**: Code formatting
- **ruff**: Fast linting with auto-fixes
- **mypy**: Type checking

Hooks run automatically on commit. Run manually:
```bash
pre-commit run --all-files
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 🤝 Contributing

We welcome contributions! This is an open source project aimed at democratizing AI radio technology.

### Areas for Contribution

1. **LLM Integration** - Expand providers and harden DJ chat beyond recommendations
2. **Music Player** - Improve streaming reliability and library UX
3. **Blockchain Integration** - Connect to real blockchain networks
4. **Dataset Loaders** - Add loaders for popular open datasets
5. **6G Protocol** - Implement 6G network protocols
6. **UI/Frontend** - Polish the Next.js player and station controls
7. **Testing** - Add comprehensive test coverage
8. **Documentation** - Improve and expand docs

## 📋 Roadmap

- [x] Core architecture and components
- [x] Personalized DJ system
- [x] Dataset management with quality scoring
- [x] Blockchain trust network
- [x] Edge device optimization
- [x] Real LLM integration (#45 / #100) — Gemini/router-backed DJ recommendations
- [x] Actual music streaming implementation (#44 / #95) — streaming API + player
- [x] Web UI for user interaction (`frontend/` Next.js 16 local player)
- [ ] Mobile app for edge devices
- [ ] Integration with public blockchains
- [ ] Community dataset marketplace
- [ ] 6G protocol implementation
- [ ] Federation with other QFZZ nodes

## 🔐 Security

QFZZ takes security seriously:
- Blockchain-verified datasets
- Trust-based community system
- Secure user identity management
- No proprietary data collection
- Open source transparency

## 📜 License

This project is open source and available under the MIT License.

## 🌍 Community

Join the QFZZ community to help build the future of personalized AI radio!

- **GitHub**: [fuzzywigg/QFZZ](https://github.com/fuzzywigg/QFZZ)
- **Issues**: Report bugs and request features
- **Discussions**: Share ideas and ask questions

## 🙏 Acknowledgments

Inspired by:
- Andon Labs Radio Eval
- The GNU/OPENSOURCE community
- Edge computing pioneers
- Blockchain innovators
- The future of 6G networks

---

**QFZZ** - *The Pulse of the Quantum Realm* 🎵✨
