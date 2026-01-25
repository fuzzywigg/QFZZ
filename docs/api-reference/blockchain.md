# BlockchainTrustNetwork, Block, and TrustRecord API Reference

## Overview

The blockchain module provides an immutable trust network for content verification using cryptographic hashing and proof-of-work mining. The `BlockchainTrustNetwork` class maintains a tamper-proof ledger of trust records for content and creators, while `Block` and `TrustRecord` classes provide the data structures for the blockchain. This enables transparent, decentralized verification of content authenticity and creator reputation.

## Table of Contents

- [BlockchainTrustNetwork Class](#blockchaintrust network-class)
  - [Constructor](#constructor)
  - [Record Management](#record-management)
  - [Verification and Reporting](#verification-and-reporting)
  - [Mining](#mining)
  - [Trust Queries](#trust-queries)
  - [Chain Validation](#chain-validation)
  - [Statistics and Export](#statistics-and-export)
- [Block Class](#block-class)
  - [Constructor](#constructor-1)
  - [Mining](#mining-1)
  - [Validation](#validation)
  - [Serialization](#serialization)
- [TrustRecord Class](#trustrecord-class)
  - [Constructor](#constructor-2)
  - [Operations](#operations)
  - [Serialization](#serialization-1)
- [Code Examples](#code-examples)
- [Architecture Details](#architecture-details)

---

## BlockchainTrustNetwork Class

### Constructor

```python
def __init__(self, difficulty: int = 2) -> None
```

Initialize a blockchain trust network with configurable mining difficulty.

**Parameters:**

- `difficulty` (int): Mining difficulty level (number of leading zeros in hash).
  - 1: Very easy (fast)
  - 2: Easy (default, ~100ms per block)
  - 3: Medium (~1s per block)
  - 4: Hard (~10s per block)
  - 5: Very hard (~1-2 min per block)

**Returns:** None

**Side Effects:**
- Creates empty blockchain chain
- Initializes pending records list
- Creates genesis block
- Initializes trust index
- Logs initialization

**Example:**

```python
from qfzz.blockchain.trust_network import BlockchainTrustNetwork

# Easy mining for testing/development
network1 = BlockchainTrustNetwork(difficulty=1)

# Default difficulty (recommended)
network2 = BlockchainTrustNetwork(difficulty=2)

# Hard mining for production (more security)
network3 = BlockchainTrustNetwork(difficulty=4)
```

---

## Record Management

### add_trust_record()

```python
def add_trust_record(self, content_id: str, creator_id: str, 
                    initial_score: float = 0.5,
                    metadata: Optional[Dict[str, Any]] = None) -> TrustRecord
```

Add a new trust record to pending records.

**Parameters:**

- `content_id` (str): Content identifier (e.g., track ID)
- `creator_id` (str): Creator identifier (e.g., artist ID)
- `initial_score` (float): Initial trust score (0.0-1.0), default 0.5 (neutral)
- `metadata` (Optional[Dict[str, Any]]): Optional metadata:
  - `source` (str): Content source
  - `verified_by` (List[str]): Verifier IDs
  - `tags` (List[str]): Content tags
  - Custom fields

**Returns:** TrustRecord - The created trust record

**Raises:**
- `ValueError`: If parameters invalid

**Side Effects:**
- Creates new TrustRecord
- Adds to pending records
- Indexes by content_id:creator_id key
- Logs creation

**Example:**

```python
network = BlockchainTrustNetwork()

# Basic record
record1 = network.add_trust_record(
    content_id="track_001",
    creator_id="artist_001"
)

# Record with custom initial score
record2 = network.add_trust_record(
    content_id="track_002",
    creator_id="artist_002",
    initial_score=0.75
)

# Record with metadata
record3 = network.add_trust_record(
    content_id="track_003",
    creator_id="artist_003",
    initial_score=0.9,
    metadata={
        "source": "verified_database",
        "verified_by": ["moderator_001", "moderator_002"],
        "tags": ["original", "licensed"],
        "submission_date": "2024-01-15"
    }
)
```

---

## Verification and Reporting

### verify_content()

```python
def verify_content(self, content_id: str, creator_id: str) -> None
```

Add verification to content, increasing trust score.

**Parameters:**

- `content_id` (str): Content identifier
- `creator_id` (str): Creator identifier

**Returns:** None

**Side Effects:**
- Creates record if doesn't exist (with initial score 0.5)
- Increments verification count
- Recalculates trust score
- Updates timestamp
- Logs verification

**Trust Score Impact:**

Each verification increases the score based on the verification/report ratio.

**Example:**

```python
# Verify content multiple times
for i in range(5):
    network.verify_content("track_001", "artist_001")

# Check updated trust score
record = network.get_trust_record("track_001", "artist_001")
print(f"Trust score: {record.trust_score:.3f}")
print(f"Verifications: {record.verifications}")
```

---

### report_content()

```python
def report_content(self, content_id: str, creator_id: str) -> None
```

Add report to content, potentially decreasing trust score.

**Parameters:**

- `content_id` (str): Content identifier
- `creator_id` (str): Creator identifier

**Returns:** None

**Side Effects:**
- Creates record if doesn't exist (with initial score 0.5)
- Increments report count
- Recalculates trust score
- Updates timestamp
- Logs report

**Trust Score Impact:**

Reports decrease score relative to verifications. Trust score is calculated as:

```
trust_score = (verifications / total) × 0.8 + 0.1
```

Where total = verifications + reports

**Example:**

```python
# Report content multiple times
for i in range(2):
    network.report_content("track_002", "artist_002")

# Check updated trust score
record = network.get_trust_record("track_002", "artist_002")
print(f"Trust score: {record.trust_score:.3f}")
print(f"Reports: {record.reports}")
```

---

## Mining

### mine_pending_records()

```python
def mine_pending_records(self) -> Optional[Block]
```

Mine all pending records into a new block and append to chain.

**Parameters:** None

**Returns:** Block - Newly mined block, or None if no pending records

**Side Effects:**
- Creates new block with pending records
- Performs proof-of-work mining (time-consuming)
- Appends block to chain
- Clears pending records
- Logs mining completion

**Proof-of-Work:** The mining process incrementally changes the nonce until the block hash has the required number of leading zeros specified by difficulty.

**Example:**

```python
# Add some records
network.add_trust_record("track_001", "artist_001")
network.add_trust_record("track_002", "artist_002")
network.verify_content("track_001", "artist_001")

print(f"Pending records: {len(network._pending_records)}")

# Mine the block
block = network.mine_pending_records()

if block:
    print(f"Block mined!")
    print(f"  Index: {block.index}")
    print(f"  Records: {len(block.records)}")
    print(f"  Hash: {block.hash}")
    print(f"  Nonce: {block.nonce}")
else:
    print("No pending records to mine")
```

---

## Trust Queries

### get_trust_score()

```python
def get_trust_score(self, content_id: str, creator_id: str) -> float
```

Get trust score for specific content from a creator.

**Parameters:**

- `content_id` (str): Content identifier
- `creator_id` (str): Creator identifier

**Returns:** float - Trust score (0.0-1.0). Returns 0.5 (neutral) if not found

**Example:**

```python
# Check trust score
score = network.get_trust_score("track_001", "artist_001")
print(f"Trust score: {score:.3f}")

# Use score for filtering
if score >= 0.7:
    print("Content is trusted")
elif score >= 0.4:
    print("Content is neutral")
else:
    print("Content is untrusted")

# Unknown content returns neutral score
unknown_score = network.get_trust_score("unknown", "unknown")
print(f"Unknown score: {unknown_score}")  # 0.5
```

---

### get_trust_record()

```python
def get_trust_record(self, content_id: str, creator_id: str) -> Optional[TrustRecord]
```

Get full trust record for specific content.

**Parameters:**

- `content_id` (str): Content identifier
- `creator_id` (str): Creator identifier

**Returns:** TrustRecord if found, None otherwise

**Example:**

```python
record = network.get_trust_record("track_001", "artist_001")

if record:
    print(f"Record ID: {record.record_id}")
    print(f"Trust Score: {record.trust_score:.3f}")
    print(f"Verifications: {record.verifications}")
    print(f"Reports: {record.reports}")
    print(f"Created: {record.created_at}")
else:
    print("Record not found")
```

---

### get_creator_trust()

```python
def get_creator_trust(self, creator_id: str) -> float
```

Get average trust score across all content from a creator.

**Parameters:**

- `creator_id` (str): Creator identifier

**Returns:** float - Average trust score (0.0-1.0), or 0.5 if no records

**Example:**

```python
# Check creator's overall reputation
creator_score = network.get_creator_trust("artist_001")
print(f"Creator {creator_score:.1%} trusted")

# Filter creators by reputation
threshold = 0.7
if creator_score >= threshold:
    print("Creator meets trust threshold")
    # Allow their content through
```

---

## Chain Validation

### is_chain_valid()

```python
def is_chain_valid(self) -> bool
```

Validate the entire blockchain for tampering.

**Parameters:** None

**Returns:** bool - True if chain valid, False if corrupted

**Validation Checks:**

1. Each block's hash is valid
2. Each block's previous_hash matches previous block's hash
3. All blocks follow difficulty requirement

**Example:**

```python
# Validate chain
if network.is_chain_valid():
    print("Blockchain is valid ✓")
else:
    print("Blockchain is corrupted ✗")

# Attempt tampering (don't do this!)
try:
    # This would be cheating:
    # network._chain[1].records[0].trust_score = 1.0
    # Now validation would fail
    if not network.is_chain_valid():
        print("Tampering detected!")
except:
    pass
```

---

## Statistics and Export

### get_chain_length()

```python
def get_chain_length(self) -> int
```

Get the length of the blockchain.

**Parameters:** None

**Returns:** int - Number of blocks in chain (includes genesis block)

**Example:**

```python
length = network.get_chain_length()
print(f"Blockchain has {length} blocks")
```

---

### get_block()

```python
def get_block(self, index: int) -> Optional[Block]
```

Retrieve a specific block by index.

**Parameters:**

- `index` (int): Block index (0 is genesis)

**Returns:** Block if found, None if out of range

**Example:**

```python
# Get first block (genesis)
genesis = network.get_block(0)
if genesis:
    print(f"Genesis block has {len(genesis.records)} records")

# Get last block
last = network.get_block(network.get_chain_length() - 1)
if last:
    print(f"Latest block: {last.hash}")
```

---

### get_latest_block()

```python
def get_latest_block(self) -> Block
```

Get the most recent block in the chain.

**Parameters:** None

**Returns:** Block - The latest block

**Example:**

```python
latest = network.get_latest_block()
print(f"Latest block index: {latest.index}")
print(f"Latest block hash: {latest.hash}")
print(f"Records in latest: {len(latest.records)}")
```

---

### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

Get comprehensive blockchain statistics.

**Parameters:** None

**Returns:** Dict containing:
- `chain_length` (int): Number of blocks
- `total_records` (int): Total trust records across all blocks
- `pending_records` (int): Records waiting to be mined
- `difficulty` (int): Mining difficulty
- `is_valid` (bool): Is blockchain valid
- `indexed_records` (int): Total unique trust records in index

**Example:**

```python
stats = network.get_statistics()
print(f"=== Blockchain Statistics ===")
print(f"Chain length: {stats['chain_length']} blocks")
print(f"Total records: {stats['total_records']}")
print(f"Pending: {stats['pending_records']}")
print(f"Difficulty: {stats['difficulty']}")
print(f"Valid: {stats['is_valid']}")
print(f"Indexed records: {stats['indexed_records']}")
```

---

### export_chain()

```python
def export_chain(self) -> List[Dict[str, Any]]
```

Export entire blockchain as list of dictionaries.

**Parameters:** None

**Returns:** List[Dict] - Serialized blocks

**Example:**

```python
import json

# Export blockchain
exported = network.export_chain()

# Save to file
with open("blockchain.json", "w") as f:
    json.dump(exported, f, indent=2)

print(f"Exported {len(exported)} blocks")
```

---

## Block Class

### Constructor

```python
@dataclass
class Block:
    index: int
    timestamp: str
    records: List[TrustRecord]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
```

Create a blockchain block.

**Parameters:**

- `index` (int): Block position in chain (0 = genesis)
- `timestamp` (str): ISO-8601 creation timestamp
- `records` (List[TrustRecord]): Trust records in block
- `previous_hash` (str): Hash of previous block ("0" for genesis)
- `nonce` (int): Nonce for proof-of-work, default 0
- `hash` (str): Block hash, computed if empty

**Returns:** None

**Side Effects:**
- Calculates hash if not provided
- Validates parameters

**Example:**

```python
from qfzz.blockchain.models import Block, TrustRecord
from datetime import datetime

# Create a genesis block (manually, normally done by network)
record1 = TrustRecord(
    record_id="rec_001",
    content_id="track_001",
    creator_id="artist_001",
    trust_score=0.5
)

genesis = Block(
    index=0,
    timestamp=datetime.now().isoformat(),
    records=[record1],
    previous_hash="0"
)

print(f"Genesis block hash: {genesis.hash}")
```

---

## Mining

### mine_block()

```python
def mine_block(self, difficulty: int = 2) -> None
```

Perform proof-of-work mining on the block.

**Parameters:**

- `difficulty` (int): Number of leading zeros required in hash

**Returns:** None

**Side Effects:**
- Incrementally increases nonce
- Recalculates hash until requirement met
- Updates block's hash

**Performance:**

- difficulty=1: ~10ms
- difficulty=2: ~100ms
- difficulty=3: ~1s
- difficulty=4: ~10s

**Example:**

```python
import time

block = Block(
    index=1,
    timestamp=datetime.now().isoformat(),
    records=[record1],
    previous_hash="abc123"
)

# Mine with difficulty 2
start = time.time()
block.mine_block(difficulty=2)
elapsed = time.time() - start

print(f"Mined in {elapsed:.3f}s")
print(f"Nonce: {block.nonce}")
print(f"Hash: {block.hash}")
print(f"Hash starts with '00': {block.hash.startswith('00')}")
```

---

## Validation

### is_valid()

```python
def is_valid(self) -> bool
```

Validate block integrity.

**Parameters:** None

**Returns:** bool - True if hash matches content, False otherwise

**Validation Check:**

Recalculates hash and compares with stored hash.

**Example:**

```python
if block.is_valid():
    print("Block is valid")
else:
    print("Block has been tampered with!")
```

---

## Serialization

### calculate_hash()

```python
def calculate_hash(self) -> str
```

Calculate SHA-256 hash of block content.

**Parameters:** None

**Returns:** str - 64-character hexadecimal hash

**Hash Input:**
```json
{
    "index": block.index,
    "timestamp": block.timestamp,
    "records": [...],
    "previous_hash": block.previous_hash,
    "nonce": block.nonce
}
```

**Example:**

```python
hash1 = block.calculate_hash()
block.nonce += 1
hash2 = block.calculate_hash()

print(f"Hash 1: {hash1}")
print(f"Hash 2: {hash2}")
print(f"Hashes different: {hash1 != hash2}")
```

---

### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

Convert block to dictionary.

**Parameters:** None

**Returns:** Dict with all block attributes

**Example:**

```python
block_dict = block.to_dict()
print(block_dict)
# {
#     'index': 0,
#     'timestamp': '2024-01-15T10:30:00',
#     'records': [...],
#     'previous_hash': '0',
#     'nonce': 42,
#     'hash': '00a1b2c3...'
# }
```

---

## TrustRecord Class

### Constructor

```python
@dataclass
class TrustRecord:
    record_id: str
    content_id: str
    creator_id: str
    trust_score: float
    verifications: int = 0
    reports: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

Create a trust record for content.

**Parameters:**

- `record_id` (str): Unique record identifier
- `content_id` (str): Content identifier
- `creator_id` (str): Creator identifier
- `trust_score` (float): Trust score (0.0-1.0)
- `verifications` (int): Verification count, default 0
- `reports` (int): Report count, default 0
- `metadata` (Dict): Additional metadata, default empty
- `created_at` (str): ISO-8601 timestamp
- `updated_at` (str): ISO-8601 timestamp

**Raises:** ValueError if validation fails

**Example:**

```python
from qfzz.blockchain.models import TrustRecord

record = TrustRecord(
    record_id="rec_001",
    content_id="track_001",
    creator_id="artist_001",
    trust_score=0.75,
    metadata={
        "source": "manual_verification",
        "tags": ["original", "licensed"]
    }
)
```

---

## Operations

### add_verification()

```python
def add_verification(self) -> None
```

Add a verification and recalculate trust score.

**Parameters:** None

**Returns:** None

**Side Effects:**
- Increments verification count
- Recalculates trust score
- Updates timestamp

**Score Recalculation:**

```
trust_score = (verifications / (verifications + reports)) × 0.8 + 0.1
```

This produces scores in range [0.1, 0.9]

**Example:**

```python
record.add_verification()
print(f"Trust score: {record.trust_score:.3f}")
```

---

### add_report()

```python
def add_report(self) -> None
```

Add a report and recalculate trust score.

**Parameters:** None

**Returns:** None

**Side Effects:**
- Increments report count
- Recalculates trust score
- Updates timestamp

**Score Recalculation:**

Same as verification, but reports decrease score.

**Example:**

```python
record.add_report()
print(f"Trust score after report: {record.trust_score:.3f}")
```

---

## Serialization

### to_dict()

```python
def to_dict(self) -> Dict[str, Any]
```

Convert record to dictionary.

**Parameters:** None

**Returns:** Dict with all record attributes

**Example:**

```python
record_dict = record.to_dict()
print(record_dict)
# {
#     'record_id': 'rec_001',
#     'content_id': 'track_001',
#     'creator_id': 'artist_001',
#     'trust_score': 0.75,
#     'verifications': 3,
#     'reports': 1,
#     'metadata': {...},
#     'created_at': '2024-01-15T10:30:00',
#     'updated_at': '2024-01-15T10:35:00'
# }
```

---

## Code Examples

### Complete Blockchain Workflow

```python
from qfzz.blockchain.trust_network import BlockchainTrustNetwork
import time

# Initialize network
network = BlockchainTrustNetwork(difficulty=2)
print(f"Initialized with difficulty: 2")

# Phase 1: Add trust records
print("\n=== Phase 1: Add Records ===")
network.add_trust_record("track_001", "artist_001", initial_score=0.6)
network.add_trust_record("track_002", "artist_002", initial_score=0.7)
network.add_trust_record("track_003", "artist_001", initial_score=0.5)

# Phase 2: Verify and report
print("\n=== Phase 2: Verify and Report ===")
network.verify_content("track_001", "artist_001")
network.verify_content("track_001", "artist_001")
network.verify_content("track_002", "artist_002")
network.report_content("track_003", "artist_001")

print(f"Pending records: {len(network._pending_records)}")

# Phase 3: Mine first block
print("\n=== Phase 3: Mine Block ===")
start = time.time()
block1 = network.mine_pending_records()
elapsed = time.time() - start

if block1:
    print(f"Block 1 mined in {elapsed:.2f}s")
    print(f"  Index: {block1.index}")
    print(f"  Records: {len(block1.records)}")
    print(f"  Hash: {block1.hash[:16]}...")

# Phase 4: Add more records and mine again
print("\n=== Phase 4: Second Block ===")
network.add_trust_record("track_004", "artist_003")
network.verify_content("track_004", "artist_003")
network.verify_content("track_004", "artist_003")

block2 = network.mine_pending_records()
if block2:
    print(f"Block 2 mined")
    print(f"  Records: {len(block2.records)}")

# Phase 5: Query trust
print("\n=== Phase 5: Query Trust ===")
score1 = network.get_trust_score("track_001", "artist_001")
score2 = network.get_trust_score("track_003", "artist_001")
creator_score = network.get_creator_trust("artist_001")

print(f"Track 1 trust: {score1:.3f}")
print(f"Track 3 trust: {score2:.3f}")
print(f"Artist 1 average: {creator_score:.3f}")

# Phase 6: Validate blockchain
print("\n=== Phase 6: Validate ===")
if network.is_chain_valid():
    print("Blockchain is valid ✓")
else:
    print("Blockchain is corrupted ✗")

# Phase 7: Statistics
print("\n=== Phase 7: Statistics ===")
stats = network.get_statistics()
print(f"Chain length: {stats['chain_length']}")
print(f"Total records: {stats['total_records']}")
print(f"Valid: {stats['is_valid']}")
```

### Filtering Content by Trust

```python
# Typical use case: Filter playlist by trust
def get_trusted_tracks(network, track_list, threshold=0.7):
    """Filter tracks by minimum trust score."""
    trusted = []
    
    for track in track_list:
        score = network.get_trust_score(
            track['content_id'],
            track['creator_id']
        )
        
        if score >= threshold:
            track['trust_score'] = score
            trusted.append(track)
    
    return trusted

# Usage
tracks = [
    {"content_id": "t1", "creator_id": "a1", "title": "Song 1"},
    {"content_id": "t2", "creator_id": "a2", "title": "Song 2"},
    {"content_id": "t3", "creator_id": "a1", "title": "Song 3"}
]

# Get only high-trust content
trusted_tracks = get_trusted_tracks(network, tracks, threshold=0.75)
print(f"Trusted: {len(trusted_tracks)}/{len(tracks)}")
```

---

## Architecture Details

### Trust Score Calculation

```
Initial: 0.5 (neutral)

After verification/reporting:
  total = verifications + reports
  if total == 0:
    score = 0.5 (neutral)
  else:
    ratio = verifications / total
    score = ratio × 0.8 + 0.1  # Range [0.1, 0.9]

Score Interpretation:
  0.0-0.2: Untrusted
  0.2-0.4: Low trust
  0.4-0.6: Neutral
  0.6-0.8: High trust
  0.8-1.0: Very high trust

Note: Calculated scores range from 0.1 to 0.9 (never reach extremes).
This sigmoid-like curve provides smoother scoring with diminishing returns
on verifications, preventing 100% scores even with many verifications.
```

### Genesis Block

Every network starts with a genesis block:
- Index: 0
- Previous Hash: "0"
- No records initially
- Hash: Calculated with mined nonce

### Mining Process

For each pending block:
1. Start with nonce = 0
2. Calculate block hash
3. Check if hash has required leading zeros
4. If not, increment nonce and repeat
5. When found, append block to chain
6. Clear pending records

### Chain Security

Security relies on:
1. Cryptographic hashing (SHA-256)
2. Proof-of-work (difficulty)
3. Chain linkage (previous_hash)
4. Immutability (changing any block breaks all subsequent blocks)

---

## Version Information

- **Module**: `qfzz.blockchain.trust_network`, `qfzz.blockchain.models`
- **Classes**: `BlockchainTrustNetwork`, `Block`, `TrustRecord`
- **Python**: 3.8+
- **Dependencies**: dataclasses, typing, datetime, hashlib, json

