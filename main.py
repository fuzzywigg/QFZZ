#!/usr/bin/env python3
"""QFZZ Radio Station Main Entry Point

Runs all demonstration scripts showcasing QFZZ capabilities.
"""

import logging
import sys

# Import all demos
from examples.basic_station import main as demo_basic_station
from examples.personalized_dj_demo import main as demo_personalized_dj
from examples.dataset_management import main as demo_dataset_management
from examples.blockchain_demo import main as demo_blockchain
from examples.edge_optimization import main as demo_edge_device

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run all QFZZ demos"""
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
