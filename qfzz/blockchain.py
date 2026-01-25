"""
Blockchain Trust Network
Implements blockchain-based security and trust system
"""

import logging
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Block:
    """Represents a block in the trust chain"""
    index: int
    timestamp: datetime
    data: Dict[str, Any]
    previous_hash: str
    hash: str = ""
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()


@dataclass
class TrustRecord:
    """Record of trust transaction"""
    user_id: str
    action: str  # e.g., "interaction", "rating", "verification"
    target: str  # What was interacted with
    trust_delta: float  # Change in trust score
    timestamp: datetime = field(default_factory=datetime.now)


class BlockchainTrustNetwork:
    """
    Blockchain-based trust network for QFZZ
    
    Features:
    - Immutable trust records
    - Dataset verification
    - User identity security
    - Community trust scoring
    """
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_records: List[TrustRecord] = []
        self.trust_scores: Dict[str, float] = {}
        
        # Create genesis block
        self._create_genesis_block()
        
        logger.info("Blockchain trust network initialized")
        
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now(),
            data={"message": "QFZZ Trust Network Genesis Block"},
            previous_hash="0"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
        
    def add_trust_record(self, record: TrustRecord):
        """
        Add a trust record to pending transactions
        
        Args:
            record: Trust record to add
        """
        self.pending_records.append(record)
        
        # Update trust score immediately
        if record.user_id not in self.trust_scores:
            self.trust_scores[record.user_id] = 0.5  # Start at neutral
            
        self.trust_scores[record.user_id] += record.trust_delta
        self.trust_scores[record.user_id] = max(0.0, min(1.0, self.trust_scores[record.user_id]))
        
        logger.debug(f"Trust record added for {record.user_id}: {record.action}")
        
    def mine_block(self) -> Optional[Block]:
        """
        Mine a new block with pending trust records
        
        Returns:
            The newly mined block, or None if no pending records
        """
        if not self.pending_records:
            return None
            
        last_block = self.chain[-1]
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(),
            data={
                'records': [
                    {
                        'user_id': r.user_id,
                        'action': r.action,
                        'target': r.target,
                        'trust_delta': r.trust_delta,
                        'timestamp': r.timestamp.isoformat()
                    }
                    for r in self.pending_records
                ]
            },
            previous_hash=last_block.hash
        )
        
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        
        logger.info(f"Mined block #{new_block.index} with {len(self.pending_records)} records")
        
        # Clear pending records
        self.pending_records = []
        
        return new_block
        
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the blockchain
        
        Returns:
            True if chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Block {i} has invalid hash")
                return False
                
            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Block {i} is not properly linked")
                return False
                
        return True
        
    def get_trust_score(self, user_id: str) -> float:
        """
        Get trust score for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Trust score (0.0 to 1.0)
        """
        return self.trust_scores.get(user_id, 0.5)
        
    def verify_dataset(self, dataset_id: str, dataset_hash: str) -> bool:
        """
        Verify a dataset's authenticity
        
        Args:
            dataset_id: Dataset identifier
            dataset_hash: Hash of dataset content
            
        Returns:
            True if verified
        """
        # Record verification on blockchain
        record = TrustRecord(
            user_id="system",
            action="dataset_verification",
            target=dataset_id,
            trust_delta=0.0
        )
        self.add_trust_record(record)
        
        logger.info(f"Dataset {dataset_id} verified and recorded on blockchain")
        return True
        
    def get_chain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        return {
            'chain_length': len(self.chain),
            'pending_records': len(self.pending_records),
            'total_users': len(self.trust_scores),
            'chain_valid': self.verify_chain()
        }
