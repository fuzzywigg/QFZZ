#!/usr/bin/env python3
"""
Example showing dataset management and blockchain verification
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import qfzz
sys.path.insert(0, str(Path(__file__).parent.parent))


from qfzz.blockchain import BlockchainTrustNetwork, TrustRecord
from qfzz.datasets import Dataset, DatasetLicense, DatasetManager


def main():
    print("=" * 60)
    print("QFZZ Dataset & Blockchain Example")
    print("=" * 60)

    # Create managers
    dataset_manager = DatasetManager(opensource_only=True, min_quality=0.7)
    blockchain = BlockchainTrustNetwork()

    # Create sample datasets
    datasets = [
        Dataset(
            id="music_001",
            name="FreeMusic Archive",
            description="Royalty-free music collection",
            license=DatasetLicense.CC_BY,
            source_url="https://freemusicarchive.org",
            quality_score=0.95,
            category="music",
            size_mb=200.0,
        ),
        Dataset(
            id="voice_001",
            name="LibriVox Audio",
            description="Public domain audiobooks and voice",
            license=DatasetLicense.PUBLIC_DOMAIN,
            source_url="https://librivox.org",
            quality_score=0.88,
            category="voice",
            size_mb=500.0,
        ),
        Dataset(
            id="conv_001",
            name="OpenSubtitles Conversations",
            description="Movie dialogue dataset",
            license=DatasetLicense.GPL,
            source_url="https://opensubtitles.org",
            quality_score=0.82,
            category="conversation",
            size_mb=350.0,
        ),
    ]

    print("\n1. Registering datasets...")
    for dataset in datasets:
        success = dataset_manager.register_dataset(dataset)
        if success:
            print(f"   ✓ Registered: {dataset.name}")

            # Verify on blockchain
            dataset_manager.verify_dataset_blockchain(dataset.id)
            blockchain.verify_dataset(dataset.id, f"hash_{dataset.id}")
            print("   ✓ Blockchain verified")

            # Add community rating
            dataset_manager.rate_dataset(dataset.id, 0.9)

            # Record trust transaction
            record = TrustRecord(
                user_id="system", action="dataset_registration", target=dataset.id, trust_delta=0.02
            )
            blockchain.add_trust_record(record)

    print("\n2. Mining blockchain block...")
    block = blockchain.mine_block()
    if block:
        print(f"   ✓ Mined block #{block.index}")
        print(f"   ✓ Block hash: {block.hash[:16]}...")

    print("\n3. Verifying blockchain integrity...")
    is_valid = blockchain.verify_chain()
    print(f"   ✓ Chain valid: {is_valid}")

    print("\n4. High quality datasets:")
    high_quality = dataset_manager.get_high_quality_datasets()
    for ds in high_quality:
        print(f"   - {ds.name}")
        print(f"     Quality: {ds.quality_score:.2f}")
        print(f"     Rating: {ds.community_rating:.2f}")
        print(f"     Verified: {'✓' if ds.verified else '✗'}")

    print("\n5. Edge-optimized datasets (max 300MB):")
    edge_datasets = dataset_manager.get_edge_optimized_datasets(max_size_mb=300)
    for ds in edge_datasets:
        print(f"   - {ds.name}: {ds.size_mb}MB")

    print("\n6. Dataset statistics:")
    stats = dataset_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n7. Blockchain statistics:")
    chain_stats = blockchain.get_chain_stats()
    for key, value in chain_stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
