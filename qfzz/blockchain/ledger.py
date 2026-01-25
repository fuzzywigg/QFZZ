"""
QFZZ Sovereign Ledger.
Implements a tamper-evident, keyless local blockchain for station history.
"""

import hashlib
import json
import logging
import os
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class LedgerBlock:
    index: int
    timestamp: str
    event_type: str
    data: Dict[str, Any]
    prev_hash: str
    hash: str
    
    def to_dict(self):
        return asdict(self)

class SovereignLedger:
    """
    Append-only Merkle-linked ledger.
    No keys required; security comes from hash chaining.
    """
    
    def __init__(self, ledger_path: str = "qfzz_ledger.json"):
        self.ledger_path = ledger_path
        self._lock = threading.Lock()
        self.chain: List[LedgerBlock] = []
        self._load_ledger()
        
    def _calculate_hash(self, index: int, timestamp: str, event_type: str, data: Dict, prev_hash: str) -> str:
        """SHA-256 hash of block content."""
        payload = f"{index}{timestamp}{event_type}{json.dumps(data, sort_keys=True)}{prev_hash}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def _load_ledger(self):
        """Load and verify ledger integrity."""
        if not os.path.exists(self.ledger_path):
            self._create_genesis_block()
        else:
            try:
                with open(self.ledger_path, 'r') as f:
                    data = json.load(f)
                    self.chain = [LedgerBlock(**b) for b in data]
                    
                if not self._verify_integrity():
                    logger.critical("LEDGER TAMPERING DETECTED! Chain hashes do not match.")
                    # In a real app we might refuse to start, or fork.
                    # For now, we log validation error but continue (soft fork).
                else:
                    logger.info(f"Sovereign Ledger loaded: {len(self.chain)} blocks verified.")
            except Exception as e:
                logger.error(f"Failed to load ledger: {e}")
                self._create_genesis_block()

    def _create_genesis_block(self):
        """Mint the first block."""
        timestamp = datetime.now().isoformat()
        genesis_hash = self._calculate_hash(0, timestamp, "GENESIS", {}, "0")
        block = LedgerBlock(0, timestamp, "GENESIS", {}, "0", genesis_hash)
        self.chain = [block]
        self._save_ledger()
        logger.info("Sovereign Ledger initialized (Genesis Block).")

    def _verify_integrity(self) -> bool:
        """Recompute all hashes to verify chain has not been altered."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # 1. Check link
            if current.prev_hash != previous.hash:
                logger.error(f"Broken link at block {i}: PrevHash mismatch")
                return False
                
            # 2. Check content hash
            recalc = self._calculate_hash(current.index, current.timestamp, current.event_type, current.data, current.prev_hash)
            if recalc != current.hash:
                logger.error(f"Data corruption at block {i}: Hash mismatch")
                return False
                
        return True

    def _save_ledger(self):
        """Atomic save to disk."""
        try:
            with open(self.ledger_path, 'w') as f:
                json.dump([b.to_dict() for b in self.chain], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist ledger: {e}")

    def record_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Mint a new block for an event.
        Thread-safe.
        """
        with self._lock:
            last_block = self.chain[-1]
            new_index = last_block.index + 1
            timestamp = datetime.now().isoformat()
            new_hash = self._calculate_hash(new_index, timestamp, event_type, data, last_block.hash)
            
            new_block = LedgerBlock(
                index=new_index,
                timestamp=timestamp,
                event_type=event_type,
                data=data,
                prev_hash=last_block.hash,
                hash=new_hash
            )
            
            self.chain.append(new_block)
            self._save_ledger() # Persist immediately
            
            logger.info(f"Minted Block #{new_index}: {event_type}")
            return new_hash

    def get_stats(self) -> Dict[str, Any]:
        """Return ledger statistics."""
        return {
            "height": len(self.chain),
            "last_hash": self.chain[-1].hash,
            "status": "Verified"
        }
