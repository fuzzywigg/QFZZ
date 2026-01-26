#!/usr/bin/env python3
"""
Example showing edge device optimization for different device types
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import qfzz
sys.path.insert(0, str(Path(__file__).parent.parent))

from qfzz.edge import EdgeDeviceConfig, EdgeOptimizer


def demo_device(name, config):
    print(f"\n{name}")
    print("-" * 40)

    optimizer = EdgeOptimizer(config)

    # Model optimization
    model_opt = optimizer.optimize_model(250.0)
    print(f"Model size: {model_opt['original_size_mb']}MB → {model_opt['target_size_mb']}MB")
    if model_opt.get("optimizations"):
        print(f"Optimizations: {', '.join(model_opt['optimizations'])}")

    # Streaming configuration
    streaming = optimizer.optimize_streaming(320)
    print(f"Bitrate: {streaming['recommended_bitrate_kbps']} kbps")
    print(f"Buffer: {streaming['buffer_ms']} ms")
    print(f"Adaptive: {streaming['adaptive_quality']}")

    # Cache some content
    optimizer.add_to_cache("track_001", {"title": "Track 1"}, 5.0)
    optimizer.add_to_cache("track_002", {"title": "Track 2"}, 5.0)
    optimizer.add_to_cache("track_003", {"title": "Track 3"}, 5.0)

    # Device status
    status = optimizer.get_device_status()
    print(f"Cache: {status['cache_items']} items ({status['cache_size_mb']}MB)")
    print(f"6G: {'Enabled' if status['6g_enabled'] else 'Disabled'}")


def main():
    print("=" * 60)
    print("QFZZ Edge Device Optimization Examples")
    print("=" * 60)

    # 1. High-end smartphone with 6G
    config1 = EdgeDeviceConfig(
        device_id="phone_001",
        device_type="smartphone",
        max_memory_mb=2048,
        max_model_size_mb=200,
        enable_6g=True,
        network_bandwidth_mbps=2000,
        storage_available_gb=8.0,
    )
    demo_device("1. High-end Smartphone (6G)", config1)

    # 2. Mid-range smartphone with 5G
    config2 = EdgeDeviceConfig(
        device_id="phone_002",
        device_type="smartphone",
        max_memory_mb=1024,
        max_model_size_mb=100,
        enable_6g=False,
        network_bandwidth_mbps=500,
        storage_available_gb=4.0,
    )
    demo_device("2. Mid-range Smartphone (5G)", config2)

    # 3. Smart speaker
    config3 = EdgeDeviceConfig(
        device_id="speaker_001",
        device_type="smart_speaker",
        max_memory_mb=512,
        max_model_size_mb=50,
        enable_6g=False,
        network_bandwidth_mbps=100,
        storage_available_gb=1.0,
    )
    demo_device("3. Smart Speaker", config3)

    # 4. Embedded device (IoT)
    config4 = EdgeDeviceConfig(
        device_id="embedded_001",
        device_type="embedded",
        max_memory_mb=256,
        max_model_size_mb=25,
        enable_6g=False,
        network_bandwidth_mbps=50,
        storage_available_gb=0.5,
    )
    demo_device("4. Embedded Device (IoT)", config4)

    # 5. Future 6G device
    config5 = EdgeDeviceConfig(
        device_id="6g_001",
        device_type="6g_device",
        max_memory_mb=4096,
        max_model_size_mb=500,
        enable_6g=True,
        network_bandwidth_mbps=5000,
        storage_available_gb=16.0,
    )
    demo_device("5. Future 6G Device", config5)

    print("\n" + "=" * 60)
    print("Edge optimization examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
