"""
External Content Fetcher for QFZZ.
Uses yt-dlp to download audio from various hosting services (YouTube, SoundCloud, etc.)
"""

import logging
import os
import yt_dlp
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ContentFetcher:
    """Fetcher for external audio content."""
    
    def __init__(self, download_dir: str = "./qfzz_audio_content"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
    def fetch_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download audio from a URL.
        Returns metadata of the downloaded track.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{self.download_dir}/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Fetching content from: {url}")
                info = ydl.extract_info(url, download=True)
                
                # Metadata mapping
                track_meta = {
                    'title': info.get('title', 'Unknown Title'),
                    'artist': info.get('uploader', 'Unknown Artist'),
                    'filename': f"{info['id']}.mp3",
                    'genre': 'External',
                    'duration': info.get('duration', 0),
                    'source_url': url
                }
                
                logger.info(f"Successfully downloaded: {track_meta['title']}")
                return track_meta
                
        except Exception as e:
            logger.error(f"Failed to fetch content: {e}")
            return None
