#!/usr/bin/env python3
"""
QFZZ Radio Station Main Entry Point
Starts the AI radio station with personalized DJ
"""

import logging
import sys
import uuid
import os
from qfzz import (
    QFZZStation, 
    StationConfig, 
    PersonalizedDJ, 
    DatasetManager,
    BlockchainTrustNetwork,
    EdgeOptimizer
)
from qfzz.datasets.models import Dataset, DatasetLicense, LicenseType
from qfzz.blockchain.models import TrustRecord
from qfzz.edge.config import EdgeDeviceConfig, DeviceType, NetworkType

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
        station_id="station_001",
        station_name="QFZZ Prime",
        enable_edge_optimization=True,
        enable_blockchain=True,
        trust_threshold=0.6,
        metadata={"tagline": "The Pulse of the Quantum Realm"}
    )
    
    station = QFZZStation(config)
    station.start()
    
    # Display status
    status = station.get_station_stats()
    logger.info(f"\nStation Status:")
    logger.info(f"  Name: {status['station_name']}")
    logger.info(f"  ID: {status['station_id']}")
    logger.info(f"  Running: {status['running']}")
    logger.info(f"  Edge Mode: {status['edge_optimization_enabled']}")
    logger.info(f"  Blockchain: {status['blockchain_enabled']}")
    
    station.stop()


def demo_personalized_dj():
    """Demonstrate personalized DJ interaction"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Personalized DJ - Demo")
    logger.info("=" * 60)
    
    # Create DJ
    # By default, it will try to use local Ollama, or fall back to Mock
    # If GEMINI_API_KEY is present, it will try connecting to that!
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        logger.info("Found GEMINI_API_KEY, attempting to use Gemini...")
    
    dj = PersonalizedDJ(llm_model="llama3", api_key=api_key)
    
    # Simulate user interaction
    user_id = "user_001"
    
    # Chat with DJ (New Feature!)
    logger.info("\n--- Chatting with DJ ---")
    greeting = dj.interact(user_id, "Yo DJ, write me a super short intro for a jazz show!")
    logger.info(f"User: Yo DJ, write me a super short intro for a jazz show!")
    logger.info(f"DJ: {greeting}")
    
    logger.info("\n--- Building Profile ---")
    # Initial preferences
    initial_prefs = {
        "genres": {"jazz": 0.8, "electronic": 0.7},
        "energy_level": 0.6,
        "discovery_factor": 0.3
    }
    
    # Get/Create profile
    profile = dj.get_or_create_profile(user_id, initial_preferences=initial_prefs)
    logger.info(f"Created profile for {user_id}")
    
    # Get recommendations
    recommendations = dj.recommend(user_id)
    
    logger.info(f"\nDJ Recommendations for {user_id}:")
    for rec in recommendations[:3]:
        logger.info(f"  - {rec['title']} by {rec['artist']} ({rec['genre']})")

    # Simulate feedback
    if recommendations:
        track = recommendations[0]
        dj.record_feedback(user_id, track['track_id'], 'like', rating=0.9)
        logger.info(f"\nUser liked: {track['title']}")
        
        # Get updated recommendations
        new_recs = dj.recommend(user_id)
        if new_recs:
            logger.info(f"New top recommendation: {new_recs[0]['title']}")


def demo_dataset_management():
    """Demonstrate dataset management"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Dataset Management - Demo")
    logger.info("=" * 60)
    
    # Create dataset manager
    manager = DatasetManager(allowed_licenses=['CC-BY', 'MIT', 'Public-Domain'])
    
    # Register some datasets
    datasets = [
        Dataset(
            dataset_id="ds_001",
            name="OpenMusic Dataset",
            description="High-quality open source music samples",
            version="1.0",
            creator_id="creator_A",
            license=DatasetLicense(
                license_type=LicenseType.CC_BY.value,
                license_url="https://creativecommons.org/licenses/by/4.0/"
            ),
            tracks=[{'title': 'Track 1', 'artist': 'Artist A', 'genre': 'Rock', 'duration': 180}], # Dummy tracks for scoring
            quality_score=0.9
        ),
        Dataset(
            dataset_id="ds_002",
            name="Conversation AI Dataset",
            description="Natural conversation training data",
            version="1.0",
            creator_id="creator_B",
            license=DatasetLicense(
                 license_type=LicenseType.MIT.value,
                 license_url="https://opensource.org/licenses/MIT"
            ),
            tracks=[{'title': 'Conv 1', 'artist': 'Speaker A', 'genre': 'Speech', 'duration': 60}],
            quality_score=0.85
        )
    ]
    
    for dataset in datasets:
        success = manager.add_dataset(dataset)
        if success:
             logger.info(f"Added {dataset.name}")
    
    # Show high quality datasets
    all_datasets = manager.list_datasets(min_quality=0.0) # Show all for demo
    logger.info(f"\nAll Datasets ({len(all_datasets)}):")
    for ds in all_datasets:
        logger.info(f"  - {ds.name} (Score: {ds.quality_score:.2f})")
    
    # Show stats
    stats = manager.get_statistics()
    logger.info(f"\nDataset Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")


def demo_blockchain():
    """Demonstrate blockchain trust network"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Blockchain Trust Network - Demo")
    logger.info("=" * 60)
    
    # Create blockchain
    blockchain = BlockchainTrustNetwork(difficulty=1) # Low difficulty for demo speed
    
    # Add trust records
    blockchain.add_trust_record("content_001", "creator_A", 0.8)
    blockchain.add_trust_record("content_002", "creator_B", 0.6)
    
    logger.info(f"\nAdded trust records to pending pool")
    
    # Mine a block
    block = blockchain.mine_pending_records()
    if block:
        logger.info(f"Mined block #{block.index} with hash: {block.hash[:10]}...")
    
    # Verify chain
    is_valid = blockchain.is_chain_valid()
    logger.info(f"Blockchain valid: {is_valid}")
    
    # Show trust scores
    score = blockchain.get_trust_score("content_001", "creator_A")
    logger.info(f"Trust Score for content_001: {score}")
    
    # Show stats
    stats = blockchain.get_statistics()
    logger.info(f"\nBlockchain Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")


def demo_edge_device():
    """Demonstrate edge device optimization"""
    logger.info("\n" + "=" * 60)
    logger.info("QFZZ Edge Device Optimization - Demo")
    logger.info("=" * 60)
    
    # Create optimizer
    optimizer = EdgeOptimizer()
    
    # Register a device
    config = EdgeDeviceConfig(
        device_id="edge_001",
        device_type=DeviceType.SMARTPHONE,
        memory_mb=4096,         # Reasonable for modern smartphone
        storage_mb=2048,        # 2GB available storage
        battery_powered=True,
        network_type=NetworkType.WIFI,
        bandwidth_mbps=50.0,
        metadata={"enable_6g": True, "max_model_size_mb": 100}
    )
    
    optimizer.register_device(config)
    
    # Optimize streaming
    optimization = optimizer.optimize_streaming("edge_001", preferences={'quality': 'high'})
    
    logger.info(f"\nStreaming Optimization for edge_001:")
    for key, value in optimization.items():
        logger.info(f"  {key}: {value}")
    
    # Simulate condition change
    logger.info("\nSimulating low battery and poor network...")
    optimizer.update_battery_status("edge_001", 0.15) # 15% battery
    optimizer.update_network_conditions("edge_001", NetworkType.CELLULAR_3G, 1.5)
    
    # Re-optimize
    new_opt = optimizer.optimize_streaming("edge_001")
    logger.info(f"New Profile: {new_opt['profile']}")
    logger.info(f"New Quality: {new_opt['quality']}")
    logger.info(f"New Bitrate: {new_opt['bitrate_kbps']} kbps")


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
