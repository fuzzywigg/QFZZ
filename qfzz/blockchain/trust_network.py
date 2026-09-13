"""
Blockchain-based trust network for content verification.
"""

import logging
from datetime import datetime
from typing import Any

from .models import Block, TrustRecord

logger = logging.getLogger(__name__)


class BlockchainTrustNetwork:
    """
    Blockchain-based trust network for immutable content verification.

    Creates tamper-proof records of trust scores for content and creators.
    """

    def __init__(self, difficulty: int = 2):
        """
        Initialize blockchain trust network.

        Args:
            difficulty: Mining difficulty (number of leading zeros)
        """
        self._chain: list[Block] = []
        self._pending_records: list[TrustRecord] = []
        self._difficulty = difficulty
        self._trust_index: dict[str, TrustRecord] = {}

        # Create genesis block
        self._create_genesis_block()
        logger.info(f"Blockchain trust network initialized (difficulty: {difficulty})")

    def _create_genesis_block(self) -> None:
        """Create the genesis block."""
        genesis = Block(
            index=0, timestamp=datetime.now().isoformat(), records=[], previous_hash="0"
        )
        genesis.mine_block(self._difficulty)
        self._chain.append(genesis)
        logger.info("Genesis block created")

    def add_trust_record(
        self,
        content_id: str,
        creator_id: str,
        initial_score: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> TrustRecord:
        """
        Add a new trust record to pending records.

        Args:
            content_id: Content identifier
            creator_id: Creator identifier
            initial_score: Initial trust score (default: 0.5)
            metadata: Optional metadata

        Returns:
            Created TrustRecord
        """
        record_id = f"{content_id}_{creator_id}_{len(self._pending_records)}"

        record = TrustRecord(
            record_id=record_id,
            content_id=content_id,
            creator_id=creator_id,
            trust_score=initial_score,
            metadata=metadata or {},
        )

        self._pending_records.append(record)
        self._trust_index[f"{content_id}:{creator_id}"] = record

        logger.debug(f"Added trust record: {record_id}")
        return record

    def verify_content(self, content_id: str, creator_id: str) -> None:
        """
        Add verification to content.

        Args:
            content_id: Content identifier
            creator_id: Creator identifier
        """
        key = f"{content_id}:{creator_id}"

        if key not in self._trust_index:
            # Create new record if doesn't exist
            self.add_trust_record(content_id, creator_id)

        record = self._trust_index[key]
        record.add_verification()
        logger.debug(f"Verified content: {content_id}")

    def report_content(self, content_id: str, creator_id: str) -> None:
        """
        Add report to content.

        Args:
            content_id: Content identifier
            creator_id: Creator identifier
        """
        key = f"{content_id}:{creator_id}"

        if key not in self._trust_index:
            # Create new record if doesn't exist
            self.add_trust_record(content_id, creator_id)

        record = self._trust_index[key]
        record.add_report()
        logger.debug(f"Reported content: {content_id}")

    def mine_pending_records(self) -> Block | None:
        """
        Mine pending records into a new block.

        Returns:
            Newly mined block, or None if no pending records
        """
        if not self._pending_records:
            logger.debug("No pending records to mine")
            return None

        previous_block = self._chain[-1]

        new_block = Block(
            index=len(self._chain),
            timestamp=datetime.now().isoformat(),
            records=self._pending_records.copy(),
            previous_hash=previous_block.hash,
        )

        # Mine the block
        new_block.mine_block(self._difficulty)

        # Add to chain
        self._chain.append(new_block)

        # Clear pending records
        self._pending_records.clear()

        logger.info(f"Mined block {new_block.index} with {len(new_block.records)} records")
        return new_block

    def get_trust_score(self, content_id: str, creator_id: str) -> float:
        """
        Get trust score for content.

        Args:
            content_id: Content identifier
            creator_id: Creator identifier

        Returns:
            Trust score (0.0-1.0), default 0.5 if not found
        """
        key = f"{content_id}:{creator_id}"

        if key in self._trust_index:
            return self._trust_index[key].trust_score

        return 0.5  # Default neutral score

    def get_trust_record(self, content_id: str, creator_id: str) -> TrustRecord | None:
        """
        Get trust record for content.

        Args:
            content_id: Content identifier
            creator_id: Creator identifier

        Returns:
            TrustRecord if found, None otherwise
        """
        key = f"{content_id}:{creator_id}"
        return self._trust_index.get(key)

    def get_creator_trust(self, creator_id: str) -> float:
        """
        Get average trust score for a creator across all content.

        Args:
            creator_id: Creator identifier

        Returns:
            Average trust score
        """
        creator_records = [
            record for record in self._trust_index.values() if record.creator_id == creator_id
        ]

        if not creator_records:
            return 0.5  # Default neutral score

        total_score = sum(record.trust_score for record in creator_records)
        return total_score / len(creator_records)

    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain.

        Returns:
            True if valid, False otherwise
        """
        for i in range(1, len(self._chain)):
            current_block = self._chain[i]
            previous_block = self._chain[i - 1]

            # Verify block hash
            if not current_block.is_valid():
                logger.error(f"Block {i} has invalid hash")
                return False

            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Block {i} has invalid previous_hash")
                return False

        return True

    def get_chain_length(self) -> int:
        """Get length of the blockchain."""
        return len(self._chain)

    def get_block(self, index: int) -> Block | None:
        """
        Get block by index.

        Args:
            index: Block index

        Returns:
            Block if found, None otherwise
        """
        if 0 <= index < len(self._chain):
            return self._chain[index]
        return None

    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self._chain[-1]

    def get_statistics(self) -> dict[str, Any]:
        """
        Get blockchain statistics.

        Returns:
            Dictionary of statistics
        """
        total_records = sum(len(block.records) for block in self._chain)

        return {
            "chain_length": len(self._chain),
            "total_records": total_records,
            "pending_records": len(self._pending_records),
            "difficulty": self._difficulty,
            "is_valid": self.is_chain_valid(),
            "indexed_records": len(self._trust_index),
        }

    def export_chain(self) -> list[dict[str, Any]]:
        """
        Export entire blockchain as list of dictionaries.

        Returns:
            List of block dictionaries
        """
        return [block.to_dict() for block in self._chain]
