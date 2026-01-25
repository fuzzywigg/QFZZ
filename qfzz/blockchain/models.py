"""
Data models for blockchain trust network.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
import hashlib
import json


@dataclass
class TrustRecord:
    """
    Trust record for content or creator.
    
    Attributes:
        record_id: Unique record identifier
        content_id: Content identifier
        creator_id: Creator identifier
        trust_score: Trust score (0.0-1.0)
        verifications: Number of verifications
        reports: Number of reports
        metadata: Additional metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    record_id: str
    content_id: str
    creator_id: str
    trust_score: float
    verifications: int = 0
    reports: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate trust record after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate trust record parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not self.record_id:
            raise ValueError("record_id must be non-empty")
        
        if not self.content_id:
            raise ValueError("content_id must be non-empty")
        
        if not self.creator_id:
            raise ValueError("creator_id must be non-empty")
        
        if not 0.0 <= self.trust_score <= 1.0:
            raise ValueError("trust_score must be between 0.0 and 1.0")
        
        if self.verifications < 0:
            raise ValueError("verifications must be non-negative")
        
        if self.reports < 0:
            raise ValueError("reports must be non-negative")
    
    def add_verification(self) -> None:
        """Add a verification to the record."""
        self.verifications += 1
        self.updated_at = datetime.now().isoformat()
        self._recalculate_trust_score()
    
    def add_report(self) -> None:
        """Add a report to the record."""
        self.reports += 1
        self.updated_at = datetime.now().isoformat()
        self._recalculate_trust_score()
    
    def _recalculate_trust_score(self) -> None:
        """Recalculate trust score based on verifications and reports."""
        total = self.verifications + self.reports
        if total == 0:
            self.trust_score = 0.5
        else:
            # Simple ratio with diminishing returns
            ratio = self.verifications / total
            # Apply sigmoid-like curve for smoother scoring
            self.trust_score = ratio * 0.8 + 0.1  # Range from 0.1 to 0.9
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trust record to dictionary."""
        return {
            'record_id': self.record_id,
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'trust_score': self.trust_score,
            'verifications': self.verifications,
            'reports': self.reports,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


@dataclass
class Block:
    """
    Blockchain block containing trust records.
    
    Attributes:
        index: Block index in chain
        timestamp: Block creation timestamp
        records: List of trust records in block
        previous_hash: Hash of previous block
        nonce: Nonce for proof of work
        hash: Block hash
    """
    
    index: int
    timestamp: str
    records: List[TrustRecord]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def __post_init__(self):
        """Calculate hash after initialization if not provided."""
        if not self.hash:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate hash of the block.
        
        Returns:
            SHA-256 hash of block data
        """
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'records': [r.to_dict() for r in self.records],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
        
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2) -> None:
        """
        Mine the block with proof of work.
        
        Args:
            difficulty: Number of leading zeros required in hash
        """
        target = '0' * difficulty
        
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def is_valid(self) -> bool:
        """
        Validate block integrity.
        
        Returns:
            True if valid, False otherwise
        """
        return self.hash == self.calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'records': [r.to_dict() for r in self.records],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
