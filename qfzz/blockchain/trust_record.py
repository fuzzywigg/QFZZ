"""Trust Record and Block Data Structures"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Block:
    """Represents a block in the trust chain

    Attributes:
        index: Block index in the chain
        timestamp: Block creation timestamp
        data: Block data payload
        previous_hash: Hash of the previous block
        hash: Hash of this block
    """

    index: int
    timestamp: datetime
    data: dict[str, Any]
    previous_hash: str
    hash: str = ""

    def calculate_hash(self) -> str:
        """Calculate block hash using SHA-256

        Returns:
            Calculated hash string
        """
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()


@dataclass
class TrustRecord:
    """Record of trust transaction

    Attributes:
        user_id: User identifier
        action: Action type (e.g., "interaction", "rating", "verification")
        target: Target of the action
        trust_delta: Change in trust score
        timestamp: Record creation timestamp
    """

    user_id: str
    action: str
    target: str
    trust_delta: float
    timestamp: datetime = field(default_factory=datetime.now)
