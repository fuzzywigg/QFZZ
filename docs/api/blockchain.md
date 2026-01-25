# Blockchain API

The blockchain module provides immutable trust records and verification.

## BlockchainTrustNetwork

::: qfzz.blockchain.trust_network.BlockchainTrustNetwork
    options:
      show_root_heading: true
      show_source: true

## TrustRecord

::: qfzz.blockchain.trust_record.TrustRecord
    options:
      show_root_heading: true
      show_source: true

## Block

::: qfzz.blockchain.trust_record.Block
    options:
      show_root_heading: true
      show_source: true

## Usage Example

```python
from qfzz import BlockchainTrustNetwork, TrustRecord

# Create blockchain
blockchain = BlockchainTrustNetwork()

# Add trust records
record = TrustRecord("user_001", "interaction", "dj", 0.05)
blockchain.add_trust_record(record)

# Mine block
block = blockchain.mine_block()
print(f"Mined block #{block.index}")

# Verify chain
is_valid = blockchain.verify_chain()
print(f"Chain valid: {is_valid}")

# Get trust score
score = blockchain.get_trust_score("user_001")
print(f"Trust score: {score}")
```
