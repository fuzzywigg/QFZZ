# QFZZ API Reference Documentation

Welcome to the comprehensive API reference for QFZZ, a quantum-fuzzy music streaming platform with personalized recommendations, blockchain-verified trust, and edge-optimized delivery.

## 📚 Documentation Files

### [1. Station API](./station.md)
**QFZZStation - Main Orchestrator**

The central hub that coordinates all QFZZ components including DJ recommendations, dataset management, blockchain trust verification, and streaming.

- **Methods**: 9 documented
- **Words**: 1,589
- **Key Topics**: Lifecycle management, listener management, playlist generation, interaction recording, statistics

**Quick Links**:
- [Constructor](./station.md#constructor)
- [Start/Stop](./station.md#core-methods)
- [Playlist Generation](./station.md#playlist-generation)

---

### [2. DJ & User Profiles API](./dj.md)
**PersonalizedDJ & UserProfile - Recommendation Engine**

AI-powered music recommendation system that learns user preferences through interaction feedback and generates personalized playlists using multi-factor scoring algorithms.

- **Methods**: 14 documented
- **Words**: 2,131
- **Key Topics**: Profile management, recommendation algorithms, feedback learning, content management

**Quick Links**:
- [Profile Management](./dj.md#profile-management)
- [Recommendation Algorithm](./dj.md#recommendations)
- [Feedback Recording](./dj.md#feedback-recording)
- [Algorithm Details](./dj.md#algorithm-details)

---

### [3. Dataset API](./datasets.md)
**DatasetManager, Dataset, DatasetLicense - Content Management**

Comprehensive dataset management system with quality scoring, license validation, and metadata analysis for music collections.

- **Methods**: 19 documented
- **Words**: 2,191
- **Key Topics**: Dataset CRUD operations, quality scoring (5-factor), license validation, metadata analysis

**Quick Links**:
- [Dataset Operations](./datasets.md#dataset-operations)
- [Quality Scoring](./datasets.md#quality-scoring)
- [License Management](./datasets.md#license-management)
- [Quality Algorithm](./datasets.md#quality-scoring-algorithm-details)

---

### [4. Blockchain API](./blockchain.md)
**BlockchainTrustNetwork, Block, TrustRecord - Immutable Trust Ledger**

Decentralized trust network using cryptographic hashing and proof-of-work mining to create tamper-proof records of content authenticity and creator reputation.

- **Methods**: 22 documented
- **Words**: 2,580
- **Key Topics**: Record management, verification/reporting, mining, validation, trust queries

**Quick Links**:
- [Record Management](./blockchain.md#record-management)
- [Mining](./blockchain.md#mining)
- [Trust Queries](./blockchain.md#trust-queries)
- [Chain Validation](./blockchain.md#chain-validation)
- [Architecture](./blockchain.md#architecture-details)

---

### [5. Edge Optimization API](./edge.md)
**EdgeOptimizer, EdgeDeviceConfig, DeviceType, NetworkType - Adaptive Streaming**

Dynamic optimization system that adapts streaming quality, buffering, caching, and bitrate based on device capabilities and network conditions.

- **Methods**: 14 documented
- **Words**: 2,202
- **Key Topics**: Device management, optimization profiles, network adaptation, battery awareness

**Quick Links**:
- [Device Management](./edge.md#device-management)
- [Optimization](./edge.md#optimization)
- [Network Updates](./edge.md#network-and-battery-updates)
- [Optimization Profiles](./edge.md#optimization-profiles)

---

## 🎯 Quick Start by Use Case

### Building a Radio Station
1. Read [Station API](./station.md) - initialization and lifecycle
2. Read [DJ API](./dj.md) - recommendation system
3. Read [Dataset API](./datasets.md) - content management
4. Read [Blockchain API](./blockchain.md) - trust verification
5. Read [Edge API](./edge.md) - client optimization

### Improving Recommendations
1. [PersonalizedDJ.recommend()](./dj.md#recommendations)
2. [UserProfile updates](./dj.md#preference-updates)
3. [Feedback recording](./dj.md#feedback-recording)
4. [Algorithm details](./dj.md#algorithm-details)

### Managing Content Quality
1. [DatasetManager.add_dataset()](./datasets.md#add_dataset)
2. [Quality scoring](./datasets.md#calculate_quality_score)
3. [License validation](./datasets.md#license-management)
4. [Statistics](./datasets.md#statistics)

### Verifying Trust
1. [BlockchainTrustNetwork](./blockchain.md#blockchaintrust-network-class)
2. [Adding trust records](./blockchain.md#record-management)
3. [Verification/reporting](./blockchain.md#verification-and-reporting)
4. [Trust queries](./blockchain.md#trust-queries)

### Optimizing for Devices
1. [Device registration](./edge.md#register_device)
2. [Streaming optimization](./edge.md#optimize_streaming)
3. [Network adaptation](./edge.md#update_network_conditions)
4. [Battery awareness](./edge.md#update_battery_status)

---

## 📊 Documentation Statistics

| API | Methods | Words | Examples | Topics |
|-----|---------|-------|----------|--------|
| Station | 9 | 1,589 | 5 | Core orchestration |
| DJ | 14 | 2,131 | 8 | Recommendations |
| Datasets | 19 | 2,191 | 6 | Content management |
| Blockchain | 22 | 2,580 | 7 | Trust verification |
| Edge | 14 | 2,202 | 8 | Streaming optimization |
| **TOTAL** | **76** | **10,693** | **34** | **5 modules** |

---

## 🔑 Key Concepts

### Multi-Factor Recommendation Scoring
Recommendations are scored using weighted factors:
- **30%** Genre matching (with genre similarity relationships)
- **25%** Artist preferences
- **20%** Energy level alignment
- **15%** Tempo matching
- **10%** Mood preferences

Plus a discovery factor (0.0-1.0) to introduce serendipity.

### Quality Score Calculation
Datasets are scored using 5 weighted factors:
- **30%** Metadata completeness (required + optional fields)
- **25%** Data consistency (field overlap, valid values)
- **20%** Dataset size (logarithmic scale)
- **15%** Diversity (unique genres and artists)
- **10%** License permissiveness

### Trust Score Calculation
Content trust scores based on verification/report ratio:
```
score = (verifications / (verifications + reports)) × 0.8 + 0.1
Range: [0.1, 0.9] with sigmoid-like curve
```

### Optimization Profiles
Four profiles for different scenarios:
- **power_save**: Low battery (128 kbps, aggressive cache)
- **balanced**: Normal usage (256 kbps, standard settings)
- **quality**: High bandwidth (320 kbps, minimal buffer)
- **bandwidth_save**: Limited data (96 kbps, large buffer)

---

## 🛠️ Common Tasks

### Add a Listener to Station
```python
from qfzz.core.station import QFZZStation
from qfzz.core.config import StationConfig

config = StationConfig(...)
station = QFZZStation(config)
station.start()
station.add_listener("user_001", preferences={"genres": {"rock": 0.8}})
```
See: [add_listener()](./station.md#add_listener)

### Generate Personalized Playlist
```python
playlist = station.generate_playlist("user_001")
# Returns list of tracks filtered by trust if blockchain enabled
```
See: [generate_playlist()](./station.md#generate_playlist)

### Record User Feedback
```python
station.record_interaction("user_001", "track_123", "like", rating=0.9)
# Updates user profile for better recommendations
```
See: [record_interaction()](./station.md#interaction-recording)

### Add Dataset with Quality Scoring
```python
from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense

manager = DatasetManager()
dataset = Dataset(...)
dataset.add_track({...})
manager.add_dataset(dataset)  # Calculates quality score
```
See: [add_dataset()](./datasets.md#add_dataset)

### Create Blockchain Record
```python
from qfzz.blockchain.trust_network import BlockchainTrustNetwork

network = BlockchainTrustNetwork(difficulty=2)
record = network.add_trust_record("content_001", "creator_001", initial_score=0.75)
network.verify_content("content_001", "creator_001")
block = network.mine_pending_records()
```
See: [add_trust_record()](./blockchain.md#add_trust_record)

### Optimize Streaming for Device
```python
from qfzz.edge.optimizer import EdgeOptimizer
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

optimizer = EdgeOptimizer()
config = EdgeDeviceConfig(
    device_id="phone_001",
    device_type=DeviceType.SMARTPHONE,
    network_type=NetworkType.WIFI
)
optimizer.register_device(config)
settings = optimizer.optimize_streaming("phone_001")
```
See: [optimize_streaming()](./edge.md#optimize_streaming)

---

## 🔗 Module Dependencies

```
QFZZStation (main orchestrator)
├── PersonalizedDJ (recommendations)
│   └── UserProfile (user preferences)
├── DatasetManager (content management)
│   └── Dataset, DatasetLicense
├── BlockchainTrustNetwork (trust verification)
│   ├── Block
│   └── TrustRecord
└── EdgeOptimizer (device optimization)
    ├── EdgeDeviceConfig
    ├── DeviceType (enum)
    └── NetworkType (enum)
```

---

## 📖 Complete Code Examples

Each API reference includes complete, runnable code examples:

### Station Workflow
See: [Complete Workflow Example](./station.md#complete-workflow-example)

### DJ Workflow
See: [Complete DJ Workflow](./dj.md#complete-dj-workflow)

### Dataset Management
See: [Complete Dataset Management Workflow](./datasets.md#complete-dataset-management-workflow)

### Blockchain Operations
See: [Complete Blockchain Workflow](./blockchain.md#complete-blockchain-workflow)

### Edge Optimization
See: [Complete Edge Optimization Workflow](./edge.md#complete-edge-optimization-workflow)

---

## 🎓 Learning Path

### Beginner
1. Start with [Station API](./station.md) to understand overall architecture
2. Learn [DJ API](./dj.md) for basic recommendations
3. Study [Edge API](./edge.md) for device optimization

### Intermediate
4. Explore [Dataset API](./datasets.md) for content management
5. Understand [Blockchain API](./blockchain.md) for trust verification
6. Combine modules in [complete examples](./station.md#complete-workflow-example)

### Advanced
7. Optimize recommendation algorithm with [feedback learning](./dj.md#feedback-recording)
8. Implement [quality scoring](./datasets.md#quality-scoring) for datasets
9. Deploy [blockchain trust](./blockchain.md#mining) for production verification
10. Fine-tune [edge profiles](./edge.md#optimization-profiles) for different networks

---

## ⚙️ System Configuration

### StationConfig
Located in `qfzz.core.config`:
- `station_id`: Unique identifier
- `station_name`: Display name
- `allowed_licenses`: List of acceptable licenses
- `enable_blockchain`: Enable trust verification
- `enable_edge_optimization`: Enable device optimization
- `trust_threshold`: Minimum trust score for content
- `max_playlist_size`: Maximum tracks per playlist
- `streaming_quality`: Default quality tier

### EdgeDeviceConfig
Located in `qfzz.edge.config`:
- `device_id`: Unique device identifier
- `device_type`: DeviceType enum value
- `network_type`: NetworkType enum value
- `bandwidth_mbps`: Available bandwidth
- `cpu_cores`: Number of CPU cores
- `memory_mb`: Available RAM
- `storage_mb`: Available storage
- `battery_powered`: Is battery device
- `battery_level`: Current battery percentage (0.0-1.0)
- `supports_hardware_decode`: Hardware decoding capable
- `max_bitrate_kbps`: Maximum bitrate supported

---

## 🚀 Best Practices

1. **Always start() and stop() stations** - Proper lifecycle management
2. **Record user interactions** - More feedback = better recommendations
3. **Validate licenses** - Ensure legal content usage
4. **Mine blockchain periodically** - Finalize trust records
5. **Monitor network conditions** - Update edge device state
6. **Check trust scores** - Filter content by reputation
7. **Test with diverse devices** - Verify edge optimization
8. **Use appropriate profiles** - Match user intent (quality vs. battery)

---

## 📝 Version Information

- **Python**: 3.8+
- **Dependencies**: dataclasses, typing, datetime, hashlib, json, logging, random, enum
- **Status**: Production-ready
- **Last Updated**: 2024-01-25

---

## 🤝 Support

For detailed information on any API:

1. **Find the relevant file** in the quick start above
2. **Use Table of Contents** for navigation
3. **Read method documentation** with parameters and returns
4. **Study code examples** for practical usage
5. **Check algorithm details** for understanding scoring/optimization

---

## 📄 License

These documentation files provide API reference for the QFZZ platform.

---

**Happy coding with QFZZ! 🎵**
