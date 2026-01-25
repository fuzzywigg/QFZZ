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
        STRICT MODE: Only whitelisted domains allowed to prevent liability.
        """
        # Trusted Public Domain / CC Sources
        # Trusted Public Domain / CC Sources
        WHITELIST = [
            # Archives
            "archive.org",
            "freemusicarchive.org",
            "musopen.org",
            "librivox.org",
            "wikipedia.org",
            "wikimedia.org",
            "gutenberg.org",
            
            # CC / Open Content
            "jamendo.com",
            "cctrax.com",
            "filmmusic.io",
            "incompetech.com",
            "audionautix.com",
            "purple-planet.com",
            "bensound.com",
            "free-stock-music.com",
            
            # Gov / Edu
            "loc.gov",
            "nasa.gov",
            "esa.int"
        ]
        
        # Check domain whitelist
        valid_domain = any(domain in url for domain in WHITELIST)
        
        if not valid_domain:
            logger.warning(f"BLOCKED: {url} is not in the trusted domain whitelist (Copyright Safety).")
            # In a real app, we would return a specific error code
            return None

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
                logger.info(f"Fetching content from SAFE source: {url}")
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
                
                logger.info(f"Successfully downloaded via yt-dlp: {track_meta['title']}")
                return track_meta
                
        except Exception as e:
            logger.warning(f"yt-dlp failed: {e}. Attempting direct download fallback...")
            
            # Fallback for direct files
            if url.lower().endswith(('.mp3', '.wav', '.ogg')):
                try:
                    import requests
                    import uuid
                    filename = f"direct_{uuid.uuid4().hex[:8]}.mp3"
                    filepath = os.path.join(self.download_dir, filename)
                    
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            
                    # Smart Metadata Parsing
                    original_name = os.path.basename(url)
                    # Decode URL encoding
                    try:
                        from urllib.parse import unquote
                        clean_name = unquote(original_name)
                    except:
                        clean_name = original_name

                    # Remove extension
                    clean_name = os.path.splitext(clean_name)[0]
                    
                    # Heuristics for Artist - Title
                    # separators: " - ", " _ ", "-", "_"
                    artist = "Unknown (Direct)"
                    title = clean_name
                    
                    for sep in [" - ", "_-_", " _ "]:
                        if sep in clean_name:
                            parts = clean_name.split(sep, 1)
                            if len(parts) == 2:
                                # Start Case
                                artist = parts[0].replace("_", " ").strip().title()
                                title = parts[1].replace("_", " ").strip().title()
                                break
                    
                    # Cleanup title if it still has underscores
                    if "_" in title:
                        title = title.replace("_", " ").title()

                    track_meta = {
                        'title': title,
                        'artist': artist,
                        'filename': filename,
                        'genre': 'External_Direct',
                        'duration': 0, 
                        'source_url': url
                    }
                    logger.info(f"Successfully downloaded via direct link: {title} by {artist}")
                    return track_meta
                    
                except Exception as direct_e:
                    logger.error(f"Direct download also failed: {direct_e}")
                    return None
            
            return None
