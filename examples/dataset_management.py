#!/usr/bin/env python3
"""Dataset Management Demo

Demonstrates dataset registration, quality scoring, and verification.
"""

import logging
from qfzz import DatasetManager, Dataset, DatasetLicense

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run dataset management demo"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Dataset Management - Demo")
    logger.info("=" * 60)
    
    # Create dataset manager
    manager = DatasetManager(opensource_only=True, min_quality=0.7)
    
    # Register some datasets
    datasets = [
        Dataset(
            id="ds_001",
            name="OpenMusic Dataset",
            description="High-quality open source music samples",
            license=DatasetLicense.CC_BY,
            source_url="https://example.com/openmusic",
            quality_score=0.9,
            category="music",
            size_mb=150.0
        ),
        Dataset(
            id="ds_002",
            name="Conversation AI Dataset",
            description="Natural conversation training data",
            license=DatasetLicense.MIT,
            source_url="https://example.com/convai",
            quality_score=0.85,
            category="conversation",
            size_mb=75.0
        ),
        Dataset(
            id="ds_003",
            name="Music Knowledge Base",
            description="Music theory and artist information",
            license=DatasetLicense.CC_BY_SA,
            source_url="https://example.com/musicknowledge",
            quality_score=0.8,
            category="knowledge",
            size_mb=50.0
        )
    ]
    
    for dataset in datasets:
        success = manager.register_dataset(dataset)
        if success:
            # Verify on blockchain
            manager.verify_dataset_blockchain(dataset.id)
            # Add community rating
            manager.rate_dataset(dataset.id, 0.85)
    
    # Show high quality datasets
    high_quality = manager.get_high_quality_datasets()
    logger.info(f"\nHigh Quality Datasets ({len(high_quality)}):")
    for ds in high_quality:
        logger.info(f"  - {ds.name} (Score: {ds.quality_score}, Verified: {ds.verified})")
    
    # Show edge-optimized datasets
    edge_datasets = manager.get_edge_optimized_datasets(max_size_mb=100)
    logger.info(f"\nEdge-Optimized Datasets ({len(edge_datasets)}):")
    for ds in edge_datasets:
        logger.info(f"  - {ds.name} ({ds.size_mb}MB)")
    
    # Show stats
    stats = manager.get_stats()
    logger.info(f"\nDataset Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Dataset management demo completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
