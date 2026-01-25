#!/usr/bin/env python3
"""
QFZZ Radio Station Main Entry Point
Starts the AI radio station with personalized DJ
"""

import logging
import sys
from qfzz import QFZZStation, PersonalizedDJ
from qfzz.core import StationConfig
from qfzz.datasets import DatasetManager, Dataset, DatasetLicense
from qfzz.blockchain import BlockchainTrustNetwork, TrustRecord
from qfzz.edge import EdgeOptimizer, EdgeDeviceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_basic_station():
    """Demonstrate basic station functionality"""
    logger.info("=" * 60)
    logger.info("QFZZ AI Radio Station - Basic Demo")
    logger.info("=" * 60)
    
    # Create and start station
    config = StationConfig(
        station_name="QFZZ",
        edge_mode=True,
        enable_6g=False,
        blockchain_enabled=True
    )
    
    station = QFZZStation(config)
    station.initialize()
    station.start()
    
    # Display status
    status = station.get_status()
    logger.info(f"\nStation Status:")
    logger.info(f"  Name: {status['name']}")
    logger.info(f"  Tagline: {status['tagline']}")
    logger.info(f"  Running: {status['running']}")
    logger.info(f"  Edge Mode: {status['edge_mode']}")
    logger.info(f"  Blockchain: {status['blockchain_enabled']}")
    
    station.stop()


def demo_personalized_dj():
    """Demonstrate personalized DJ interaction"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Personalized DJ - Demo")
    logger.info("=" * 60)
    
    # Create DJ
    dj = PersonalizedDJ(name="DJ Quantum", edge_mode=True)
    
    # Simulate user interaction
    user_id = "user_001"
    
    # First interaction
    greeting = dj.greet_user(user_id, "Alex")
    logger.info(f"\nDJ: {greeting}")
    
    # User asks for music
    response = dj.interact(user_id, "Can you recommend some music?")
    logger.info(f"\nUser: Can you recommend some music?")
    logger.info(f"DJ: {response}")
    
    # Update preferences
    dj.update_preferences(user_id, ["jazz", "electronic", "ambient"])
    
    # Ask again
    response = dj.interact(user_id, "Play something for me")
    logger.info(f"\nUser: Play something for me")
    logger.info(f"DJ: {response}")
    
    # Check trust score
    trust = dj.get_trust_score(user_id)
    logger.info(f"\nUser Trust Score: {trust:.2f}")


def demo_dataset_management():
    """Demonstrate dataset management"""
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


def demo_blockchain():
    """Demonstrate blockchain trust network"""
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
    logger.info(f"\nTrust Scores:")
    for user_id in ["user_001", "user_002"]:
        score = blockchain.get_trust_score(user_id)
        logger.info(f"  {user_id}: {score:.2f}")
    
    # Show stats
    stats = blockchain.get_chain_stats()
    logger.info(f"\nBlockchain Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")


def demo_edge_device():
    """Demonstrate edge device optimization"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Edge Device Optimization - Demo")
    logger.info("=" * 60)
    
    # Create edge device config
    config = EdgeDeviceConfig(
        device_id="edge_001",
        device_type="smartphone",
        max_memory_mb=512,
        max_model_size_mb=100,
        enable_6g=True,
        network_bandwidth_mbps=1000,
        storage_available_gb=2.0
    )
    
    # Create optimizer
    optimizer = EdgeOptimizer(config)
    
    # Optimize model
    model_optimization = optimizer.optimize_model(250.0)
    logger.info(f"\nModel Optimization:")
    for key, value in model_optimization.items():
        logger.info(f"  {key}: {value}")
    
    # Optimize streaming
    streaming_config = optimizer.optimize_streaming(320)
    logger.info(f"\nStreaming Configuration:")
    for key, value in streaming_config.items():
        logger.info(f"  {key}: {value}")
    
    # Test caching
    optimizer.add_to_cache("track_001", {"title": "Test Track"}, 5.0)
    optimizer.add_to_cache("track_002", {"title": "Another Track"}, 5.0)
    
    # Get device status
    status = optimizer.get_device_status()
    logger.info(f"\nDevice Status:")
    for key, value in status.items():
        logger.info(f"  {key}: {value}")


def main():
    """Run all demos"""
    try:
        demo_basic_station()
        demo_personalized_dj()
        demo_dataset_management()
        demo_blockchain()
        demo_edge_device()
        
        logger.info("\n" + "=" * 60)
        logger.info("All demos completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error running demos: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
