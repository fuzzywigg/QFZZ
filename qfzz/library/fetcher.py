"""
External Content Fetcher for QFZZ.
Uses yt-dlp to download audio from various hosting services (YouTube, SoundCloud, etc.)
"""

import logging
import os
from typing import Any, Optional

import yt_dlp

logger = logging.getLogger(__name__)


class ContentFetcher:
    """Fetcher for external audio content."""

    def __init__(self, download_dir: str = "./qfzz_audio_content"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

    def fetch_from_url(self, url: str) -> Optional[dict[str, Any]]:
        """
        Download audio from a URL.
        Relaxed Mode: Warns on non-whitelisted domains but allows specific user overrides.
        """
        # Trusted Public Domain / CC Sources (Verified Safe)
        VERIFIED_DOMAINS = [
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
            "tribeofnoise.com",  # Added per user request
            # Gov / Edu
            "loc.gov",
            "nasa.gov",
            "esa.int",
        ]

        # Check domain whitelist
        is_verified = any(domain in url for domain in VERIFIED_DOMAINS)

        if not is_verified:
            logger.warning(
                f"CAUTION: {url} is not in the verified domain list. Proceeding with caution."
            )
            # We no longer strictly block, but we mark it.

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": f"{self.download_dir}/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            # Add User-Agent to yt-dlp to avoid blocks
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Attempting fetch from source: {url}")
                info = ydl.extract_info(url, download=True)

                # Metadata mapping
                track_meta = {
                    "title": info.get("title", "Unknown Title"),
                    "artist": info.get("uploader", info.get("artist", "Unknown Artist")),
                    "filename": f"{info['id']}.mp3",
                    "genre": "External" if is_verified else "External_Unverified",
                    "duration": info.get("duration", 0),
                    "source_url": url,
                }

                logger.info(f"Successfully downloaded via yt-dlp: {track_meta['title']}")
                return track_meta

        except Exception as e:
            logger.warning(f"yt-dlp failed: {e}. Attempting direct download fallback...")

            # Fallback for direct files (and some others if we can scrape)
            # We allow fallback if it LOOKS like a file or if the user forced it
            if True:  # Always try fallback if yt-dlp fails, worst case it fails too
                try:
                    import re
                    import uuid
                    from urllib.parse import unquote

                    import requests

                    filename = f"direct_{uuid.uuid4().hex[:8]}.mp3"
                    filepath = os.path.join(self.download_dir, filename)

                    # Add headers to direct request
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }

                    # Verify content type before downloading big files
                    head_resp = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
                    content_type = head_resp.headers.get("Content-Type", "").lower()

                    if "html" in content_type and not url.lower().endswith(
                        (".mp3", ".wav", ".ogg")
                    ):
                        # It's an HTML page and we failed yt-dlp.
                        # We can't do magic here without more complex scrapers.
                        logger.error("URL is HTML and yt-dlp failed. Cannot extract audio.")
                        return None

                    response = requests.get(url, stream=True, headers=headers, timeout=30)
                    response.raise_for_status()

                    with open(filepath, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Smart Metadata Parsing
                    original_name = os.path.basename(url)
                    # Decode URL encoding
                    try:
                        clean_name = unquote(original_name)
                    except:
                        clean_name = original_name

                    # Remove extension
                    clean_name = os.path.splitext(clean_name)[0]

                    # Normalize separators
                    # Replace underscores with spaces for clearer extraction, unless it looks like a specifically formatted ID
                    clean_name_spaces = clean_name.replace("_", " ").replace("-", " - ")

                    # Heuristics for Artist - Title
                    # We assume "Artist - Title" format often
                    artist = "Unknown Artist"
                    title = clean_name

                    # Try splitting by " - " (which we ensured exists for dashes)
                    parts = clean_name_spaces.split(" - ")
                    if len(parts) >= 2:
                        artist = parts[0].strip().title()
                        title = " - ".join(parts[1:]).strip().title()
                    elif " by " in clean_name_spaces.lower():
                        parts = re.split(r" by ", clean_name_spaces, flags=re.IGNORECASE)
                        title = parts[0].strip().title()
                        artist = parts[1].strip().title()

                    # Cleanup title
                    if "_" in title:
                        title = title.replace("_", " ").title()

                    # Remove common junk from title
                    title = re.sub(
                        r"\s*\(.*?\)", "", title
                    ).strip()  # Remove parenthesis content like (Original Mix)

                    track_meta = {
                        "title": title,
                        "artist": artist,
                        "filename": filename,
                        "genre": "External_Direct" if is_verified else "External_Direct_Unverified",
                        "duration": 0,
                        "source_url": url,
                    }
                    logger.info(f"Successfully downloaded via direct link: {title} by {artist}")
                    return track_meta

                except Exception as direct_e:
                    logger.error(f"Direct download also failed: {direct_e}")
                    return None

            return None
