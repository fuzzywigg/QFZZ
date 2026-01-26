#!/usr/bin/env python3
"""Edge Device Optimization Demo

Demonstrates edge device optimization for models, streaming, and caching.
"""

import logging

from qfzz import EdgeDeviceConfig, EdgeOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Run edge device demo"""
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
        storage_available_gb=2.0,
    )

    # Create optimizer
    optimizer = EdgeOptimizer(config)

    # Optimize model
    model_optimization = optimizer.optimize_model(250.0)
    logger.info("\nModel Optimization:")
    for key, value in model_optimization.items():
        logger.info(f"  {key}: {value}")

    # Optimize streaming
    streaming_config = optimizer.optimize_streaming(320)
    logger.info("\nStreaming Configuration:")
    for key, value in streaming_config.items():
        logger.info(f"  {key}: {value}")

    # Test caching
    optimizer.add_to_cache("track_001", {"title": "Test Track"}, 5.0)
    optimizer.add_to_cache("track_002", {"title": "Another Track"}, 5.0)

    # Get device status
    status = optimizer.get_device_status()
    logger.info("\nDevice Status:")
    for key, value in status.items():
        logger.info(f"  {key}: {value}")

    logger.info("\n" + "=" * 60)
    logger.info("Edge optimization demo completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
