# Ledger Verification Guide

Complete guide for verifying QFZZ blockchain ledger integrity.

## Overview

The QFZZ ledger verification tool validates the SHA-256 hash chain integrity of the blockchain ledger (`qfzz_ledger.json`). This ensures that no tampering or corruption has occurred in the immutable audit trail.

## Quick Start

### Basic Verification

```bash
# Verify the default ledger
python scripts/verify-ledger.py

# Verify specific ledger file
python scripts/verify-ledger.py path/to/qfzz_ledger.json

# Quiet mode (errors only)
python scripts/verify-ledger.py -q

# Verbose mode
python scripts/verify-ledger.py -v
```

### Get Statistics

```bash
python scripts/verify-ledger.py --stats
```

Output:
```json
{
  "total_blocks": 23,
  "genesis_block": "2026-01-25T13:38:04.389662",
  "latest_block": "2026-01-25T15:21:07.038891",
  "first_index": 0,
  "last_index": 22,
  "has_gaps": false,
  "is_valid": true
}
```

### Export Report

```bash
python scripts/verify-ledger.py -o verification_report.json
```

This creates a detailed JSON report with:
- Verification timestamp
- Statistics
- All errors found
- All warnings found
- Overall validity status

## How It Works

### Hash Chain Verification

The ledger uses SHA-256 hashing to create an immutable chain:

```
Block 0 (Genesis)
  ├─ hash: SHA256(index + timestamp + event_type + data + prev_hash)
  └─ prev_hash: "0"

Block 1
  ├─ hash: SHA256(index + timestamp + event_type + data + prev_hash)
  └─ prev_hash: <hash from Block 0>

Block 2
  ├─ hash: SHA256(index + timestamp + event_type + data + prev_hash)
  └─ prev_hash: <hash from Block 1>
```

Any modification to a block changes its hash, which breaks the chain.

### Verification Steps

1. **Load Ledger**: Parse JSON file
2. **Verify Genesis Block**: Check first block structure
3. **Verify Hashes**: Recalculate each block's hash
4. **Verify Chain Links**: Ensure prev_hash matches previous block
5. **Verify Timestamps**: Check temporal ordering
6. **Generate Report**: Compile results

## Ledger Format

### QFZZ Ledger Structure

```json
[
  {
    "index": 0,
    "timestamp": "2026-01-25T13:38:04.389662",
    "event_type": "GENESIS",
    "data": {},
    "prev_hash": "0",
    "hash": "4b6141a44349a600dcf7dc5e82ede04aa1dea97ab84261fa35779ef9ef8e7068"
  },
  {
    "index": 1,
    "timestamp": "2026-01-25T13:38:30.462963",
    "event_type": "SEGUE_GENERATION",
    "data": {
      "prev_track": "Station Intro",
      "next_track": "test_tone",
      "prompt_hash": -3680754532741554151
    },
    "prev_hash": "4b6141a44349a600dcf7dc5e82ede04aa1dea97ab84261fa35779ef9ef8e7068",
    "hash": "07fe7e6261a3ac7874936534e3e4ff9ce1dd7f3576639f1a8bf5e8ba4effbfd3"
  }
]
```

### Required Fields

- `index`: Block number (integer, sequential)
- `timestamp`: ISO 8601 format string
- `event_type`: Type of event (string)
- `data`: Event-specific data (object)
- `prev_hash`: Previous block hash (or "0" for genesis)
- `hash`: This block's hash (SHA-256 hex)

## Continuous Monitoring

### Monitor Script

Run continuous verification:

```bash
./scripts/monitor-ledger.sh
```

This will:
- Check ledger every 60 seconds (configurable)
- Log all verifications
- Alert on failures

### Custom Interval

```bash
CHECK_INTERVAL=30 ./scripts/monitor-ledger.sh
```

### Run as Service

Create systemd service `/etc/systemd/system/qfzz-ledger-monitor.service`:

```ini
[Unit]
Description=QFZZ Ledger Verification Monitor
After=network.target

[Service]
Type=simple
User=qfzz
WorkingDirectory=/opt/qfzz
ExecStart=/opt/qfzz/scripts/monitor-ledger.sh
Restart=always
RestartSec=10
Environment="CHECK_INTERVAL=60"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable qfzz-ledger-monitor
sudo systemctl start qfzz-ledger-monitor
sudo systemctl status qfzz-ledger-monitor
```

## Integration

### Python API

```python
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from verify_ledger import LedgerVerifier

# Create verifier
verifier = LedgerVerifier("qfzz_ledger.json")

# Run verification
is_valid = verifier.verify_all()

if is_valid:
    print("✓ Ledger is valid")
else:
    print("✗ Ledger is invalid")
    for error in verifier.errors:
        print(f"  - {error}")

# Get statistics
stats = verifier.get_statistics()
print(f"Total blocks: {stats['total_blocks']}")
print(f"Genesis: {stats['genesis_block']}")
```

### Automated Testing

Add to your test suite:

```python
import unittest
from verify_ledger import LedgerVerifier

class TestLedgerIntegrity(unittest.TestCase):
    def test_ledger_valid(self):
        """Verify ledger integrity."""
        verifier = LedgerVerifier("qfzz_ledger.json")
        self.assertTrue(verifier.verify_all())
```

### CI/CD Integration

#### GitHub Actions

```yaml
name: Verify Ledger

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Verify Ledger
        run: python scripts/verify-ledger.py qfzz_ledger.json
```

#### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python scripts/verify-ledger.py --quiet || {
    echo "ERROR: Ledger verification failed!"
    exit 1
}
```

## Troubleshooting

### Hash Mismatch Errors

**Problem**: Blocks report hash mismatches

**Causes**:
- Ledger file corrupted
- Manual editing of ledger
- Software bug in block creation

**Solution**:
1. Check if file is corrupted: `cat qfzz_ledger.json | jq`
2. If manual edit: Restore from backup
3. If software bug: Report issue

### Chain Break Errors

**Problem**: prev_hash doesn't match previous block

**Causes**:
- Blocks inserted out of order
- Blocks deleted
- Concurrent writes without locking

**Solution**:
1. Identify where chain breaks
2. Restore from last known good backup
3. Implement proper file locking

### Timestamp Warnings

**Problem**: Timestamps go backwards

**Causes**:
- System clock changed
- Timezone issues
- Testing with mock data

**Solution**:
- Usually harmless (warning only)
- Fix system clock
- Document if intentional (testing)

### Genesis Block Issues

**Problem**: Genesis block has non-standard format

**Causes**:
- Different blockchain implementation
- Migration from old format

**Solution**:
- Usually harmless (warning only)
- Document the format difference

## Security Considerations

### What Verification Proves

✅ **Guarantees**:
- No tampering since last valid state
- Chain integrity intact
- All hashes mathematically correct

❌ **Does NOT guarantee**:
- Content accuracy (garbage in, garbage out)
- Authorization of changes
- Correct initial data

### Best Practices

1. **Regular Verification**
   - Run verification frequently (every minute)
   - Log all verifications
   - Alert on failures

2. **Backup Strategy**
   - Keep verified backups
   - Store in multiple locations
   - Test restore procedures

3. **Access Control**
   - Limit write access to ledger file
   - Use file permissions (read-only for most users)
   - Audit file access

4. **Monitoring**
   - Continuous verification
   - Alert on anomalies
   - Track verification history

5. **Incident Response**
   - Plan for integrity failures
   - Have rollback procedures
   - Document recovery process

## Advanced Usage

### Batch Verification

Verify multiple ledgers:

```bash
for ledger in ledgers/*.json; do
    echo "Verifying $ledger..."
    python scripts/verify-ledger.py "$ledger" --quiet || echo "FAILED: $ledger"
done
```

### Scheduled Verification

Add to crontab:

```bash
# Verify every hour
0 * * * * cd /opt/qfzz && python scripts/verify-ledger.py -q -o /tmp/verify.json

# Send daily summary
0 0 * * * cd /opt/qfzz && python scripts/verify-ledger.py --stats | mail -s "QFZZ Ledger Stats" admin@example.com
```

### Network Verification

Verify ledgers across multiple nodes:

```bash
#!/bin/bash
NODES=("node1.example.com" "node2.example.com" "node3.example.com")

for node in "${NODES[@]}"; do
    echo "Checking $node..."
    ssh "$node" "cd /opt/qfzz && python scripts/verify-ledger.py"
done
```

## API Reference

### LedgerVerifier Class

```python
class LedgerVerifier:
    def __init__(self, ledger_path: str)
    def load_ledger(self) -> bool
    def verify_block_hash(self, block: Block) -> bool
    def verify_chain_links(self) -> bool
    def verify_genesis_block(self) -> bool
    def verify_timestamps(self) -> bool
    def verify_all(self) -> bool
    def get_statistics(self) -> dict
    def export_report(self, output_path: str) -> None
```

### Block Class

```python
@dataclass
class Block:
    index: int
    timestamp: str
    data: dict
    previous_hash: str
    hash: str
    event_type: Optional[str]
    
    @classmethod
    def from_dict(cls, d: dict) -> 'Block'
    def calculate_hash(self) -> str
    def is_valid(self) -> bool
```

## Resources

- **Bitcoin Whitepaper**: Original blockchain concept
- **Merkle Trees**: Hash tree structures
- **SHA-256**: Cryptographic hash function
- **QFZZ Repository**: https://github.com/fuzzywigg/QFZZ

## Support

For issues with verification:
- Check this guide first
- Verify file format matches specification
- Run with `-v` for verbose output
- Open issue on GitHub: https://github.com/fuzzywigg/QFZZ/issues

---

**Remember**: A valid ledger only proves integrity, not content accuracy. Always validate the source and authorization of data.
