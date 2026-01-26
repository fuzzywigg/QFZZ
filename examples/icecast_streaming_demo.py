#!/usr/bin/env python3
"""
QFZZ Icecast Streaming Demo

Demonstrates streaming to Icecast server with the new client.
"""

import logging
import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qfzz.streaming import IcecastClient, IcecastConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run Icecast streaming demo."""
    logger.info("=" * 60)
    logger.info("QFZZ Icecast Streaming Demo")
    logger.info("=" * 60)
    
    # Check if Icecast server is accessible
    logger.info("This demo requires a running Icecast server")
    logger.info("Start with: ./scripts/start-icecast.sh")
    logger.info("")
    
    # Configure Icecast connection
    config = IcecastConfig(
        host="localhost",
        port=8000,
        password="hackme",
        mount="/qfzz",
        name="QFZZ Demo Stream",
        description="Demonstrating Icecast streaming",
        genre="Electronic/AI",
        format="mp3",
        bitrate=128,
    )
    
    # Create client
    client = IcecastClient(config)
    
    # Try to connect
    logger.info(f"Connecting to Icecast at {config.host}:{config.port}{config.mount}...")
    if not client.connect():
        logger.error("Failed to connect to Icecast server")
        logger.error("Make sure Icecast is running: ./scripts/start-icecast.sh")
        return 1
    
    logger.info("Connected successfully!")
    logger.info("")
    logger.info("Stream URL: http://localhost:8000/qfzz")
    logger.info("Admin URL: http://localhost:8000/admin/")
    logger.info("")
    
    # Update metadata
    test_track = {
        "title": "Quantum Resonance",
        "artist": "QFZZ AI",
        "album": "The Pulse",
        "genre": "Electronic",
    }
    
    client.update_metadata(test_track)
    logger.info(f"Now playing: {test_track['artist']} - {test_track['title']}")
    
    # Stream test audio
    audio_dir = Path(__file__).parent.parent / "qfzz_audio_content"
    test_files = [
        audio_dir / "test_tone.wav",
        audio_dir / "intro.wav",
    ]
    
    # Check for available audio files
    available_files = [f for f in test_files if f.exists()]
    
    if not available_files:
        logger.warning("No test audio files found in qfzz_audio_content/")
        logger.info("Generating test content...")
        
        # Generate test content
        from qfzz.streaming.audio_tools import generate_tone
        audio_dir.mkdir(exist_ok=True)
        generate_tone(str(audio_dir / "test_tone.wav"), duration_sec=10, freq_hz=440)
        generate_tone(str(audio_dir / "intro.wav"), duration_sec=5, freq_hz=554)
        available_files = test_files
    
    # Stream files
    logger.info(f"Streaming {len(available_files)} test files...")
    for audio_file in available_files:
        logger.info(f"Streaming: {audio_file.name}")
        if not client.stream_file(str(audio_file), chunk_size=4096):
            logger.error("Streaming failed")
            break
        time.sleep(0.5)  # Brief pause between tracks
    
    # Show statistics
    stats = client.get_stats()
    logger.info("")
    logger.info("Streaming Statistics:")
    logger.info(f"  State: {stats['state']}")
    logger.info(f"  Bytes sent: {stats['bytes_sent']:,}")
    logger.info(f"  Uptime: {stats['uptime_seconds']:.1f}s")
    
    # Disconnect
    logger.info("")
    logger.info("Disconnecting...")
    client.disconnect()
    logger.info("Demo complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
