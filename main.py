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
    
    # Music Player (Port 8001)
    player = MusicPlayer(content_dir=AUDIO_DIR, port=8001)
    
    # Initialize Playlist
    playlist = [
        {'title': 'Station Intro', 'artist': 'QFZZ AI', 'filename': 'intro.wav', 'genre': 'Station ID', 'duration': 3},
        {'title': 'Test Tone 440Hz', 'artist': 'Physics', 'filename': 'test_tone.wav', 'genre': 'Test', 'duration': 5}
    ]
    player.load_playlist(playlist)
    
    # DJ
    api_key = os.environ.get("GEMINI_API_KEY")
    dj = PersonalizedDJ(llm_model="llama3", api_key=api_key)
    
    # CONNECT components: Allow Server to talk to DJ and Player
    player.server.attach_instances(dj, player)
    
    # 2. Content Ingestion (Deep Scan)
    logger.info("Scanning library for content...")
    scanned_tracks = dj.scanner.scan_directory()
    
    # Merge scanned tracks with basic playlist
    # (If scanned tracks exist, prefer them over basic test tones if matched)
    if scanned_tracks:
        logger.info(f"Ingested {len(scanned_tracks)} tracks from local library")
        # Update playlist with scanned tracks (converting to player format)
        new_playlist = []
        for track in scanned_tracks:
            # Map scanner metadata to player format
            p_track = {
                'title': track['title'],
                'artist': track['artist'],
                'filename': track['filename'],
                'genre': track['genre'],
                'duration': track['fingerprint']['duration'] if track['fingerprint'] else 0
            }
            new_playlist.append(p_track)
        
        # Merge or replace? Let's just append for now to keep Intro
        playlist.extend(new_playlist)
        player.load_playlist(playlist)

    # Populate Knowledge Graph with ALL tracks (including deep features)
    for track in playlist:
        # Check if we have deep metadata in scanned_tracks
        deep_meta = next((t for t in scanned_tracks if t['filename'] == track['filename']), None)
        
        dj.kg.add_track_node(
            track_id=track['filename'], # unique id
            metadata=deep_meta if deep_meta else track
        )
        
    if api_key:
        logger.info("DJ connected to Gemini Cloud")
    else:
        logger.info("DJ using local fallback")
        
    # Expose Knowledge Graph
    player.server.set_graph(dj.kg.export_d3_json())
    logger.info("Knowledge Graph API enabled")
    
    # Generate Initial Segue (Test)
    if len(playlist) >= 2:
        try:
            # We need deep metadata for this to be good
            t1 = playlist[0]
            t2 = playlist[1]
            
            # Find deep meta for t1/t2
            dm1 = next((t for t in scanned_tracks if t['filename'] == t1['filename']), None) 
            dm2 = next((t for t in scanned_tracks if t['filename'] == t2['filename']), None)
            
            # Use deep meta if available, else basic
            segue = dj.generate_segue(
                track_prev=dm1 if dm1 else t1, 
                track_next=dm2 if dm2 else t2
            )
            logger.info(f"DJ Segue: {segue}")
            player.set_dj_message(segue)
        except Exception as e:
            logger.error(f"DJ failed to speak: {e}")

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
            # Update Ledger Status on Frontend
            if hasattr(dj, 'ledger'):
                player.set_ledger_stats(dj.ledger.get_stats())
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        station.stop()
        # player cleanup handles server shutdown
        sys.exit(0)

if __name__ == "__main__":
    main()
