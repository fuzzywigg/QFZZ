#!/usr/bin/env python3
"""Basic QFZZ Radio Station Demo

Demonstrates basic station setup and functionality.
"""

import logging
from qfzz import QFZZStation, StationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run basic station demo"""
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
    
    logger.info("\n" + "=" * 60)
    logger.info("Basic demo completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
