"""
QFZZ Server Runner
Starts the entire system and keeps it running for frontend interaction.
"""

import logging
import time
import os
import signal
import sys
from qfzz import (
    QFZZStation, 
    StationConfig, 
    PersonalizedDJ, 
    DatasetManager,
    BlockchainTrustNetwork
)
from qfzz.streaming import MusicPlayer
from qfzz.datasets.models import Dataset, DatasetLicense, LicenseType

# Configure output folder
AUDIO_DIR = "./qfzz_audio_content"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting QFZZ Server...")
    
    # 1. Initialize Components
    
    # Music Player (Port 8000)
    player = MusicPlayer(content_dir=AUDIO_DIR, port=8000)
    
    # Initialize Playlist
    playlist = [
        {'title': 'Station Intro', 'artist': 'QFZZ AI', 'filename': 'intro.wav', 'genre': 'Station ID', 'duration': 3},
        {'title': 'Test Tone 440Hz', 'artist': 'Physics', 'filename': 'test_tone.wav', 'genre': 'Test', 'duration': 5}
    ]
    player.load_playlist(playlist)
    
    # DJ
    api_key = os.environ.get("GEMINI_API_KEY")
    dj = PersonalizedDJ(llm_model="llama3", api_key=api_key)
    if api_key:
        logger.info("DJ connected to Gemini Cloud")
    else:
        logger.info("DJ using local fallback")

    # Station Core
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
    
    logger.info("="*60)
    logger.info("QFZZ SYSTEM ONLINE")
    logger.info("Backend API/Stream: http://localhost:8000")
    logger.info("Frontend App:       http://localhost:3000")
    logger.info("="*60)
    logger.info("Press Ctrl+C to stop")
    
    # Keep alive loop
    try:
        while True:
            time.sleep(1)
            # Here we could process background tasks
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        station.stop()
        # player cleanup handles server shutdown
        sys.exit(0)

if __name__ == "__main__":
    main()
