#!/usr/bin/env python3
"""Blockchain Trust Network Demo

Demonstrates blockchain-based trust recording and verification.
"""

import logging

from qfzz import BlockchainTrustNetwork, TrustRecord

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Run blockchain demo"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Blockchain Trust Network - Demo")
    logger.info("=" * 60)

    # Create blockchain
    blockchain = BlockchainTrustNetwork()

    # Add trust records
    records = [
        TrustRecord("user_001", "interaction", "dj", 0.05),
        TrustRecord("user_001", "rating", "dataset_001", 0.03),
        TrustRecord("user_002", "interaction", "dj", 0.05),
        TrustRecord("user_002", "verification", "dataset_002", 0.02),
    ]

    for record in records:
        blockchain.add_trust_record(record)

    logger.info(f"\nAdded {len(records)} trust records")

    # Mine a block
    block = blockchain.mine_block()
    if block:
        logger.info(f"Mined block #{block.index}")

    # Verify chain
    is_valid = blockchain.verify_chain()
    logger.info(f"Blockchain valid: {is_valid}")

    # Show trust scores
    logger.info("\nTrust Scores:")
    for user_id in ["user_001", "user_002"]:
        score = blockchain.get_trust_score(user_id)
        logger.info(f"  {user_id}: {score:.2f}")

    # Show stats
    stats = blockchain.get_chain_stats()
    logger.info("\nBlockchain Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    logger.info("\n" + "=" * 60)
    logger.info("Blockchain demo completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
