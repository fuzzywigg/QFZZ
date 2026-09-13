"""
QFZZ Content Ingestion and Analysis.
Extracts 'Sonic Fingerprints' from audio files to power the Knowledge Graph.
"""

import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import librosa
import mutagen
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SonicFingerprint:
    """Spectral and rhythmic features of a track."""

    bpm: float
    duration: float
    key: str
    energy: float
    danceability: float
    loudness: float

    def to_dict(self):
        return asdict(self)


class ContentScanner:
    """
    Intelligent audio scanner that extracts deep features from content.
    """

    def __init__(self, library_path: str):
        self.library_path = os.path.abspath(library_path)
        os.makedirs(self.library_path, exist_ok=True)

    def scan_file(self, filename: str) -> dict[str, Any] | None:
        """
        Deep analysis of a single audio file.
        Returns a rich metadata dictionary ready for the Knowledge Graph.
        """
        file_path = os.path.join(self.library_path, filename)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        try:
            logger.info(f"Analyzing sonic signature of: {filename}...")

            # 1. Basic Metadata (Mutagen)
            # This handles ID3 tags from MP3s, etc.
            meta = mutagen.File(file_path, easy=True)
            title = (
                meta.get("title", [os.path.splitext(filename)[0]])[0]
                if meta
                else os.path.splitext(filename)[0]
            )
            artist = meta.get("artist", ["Unknown Artist"])[0] if meta else "Unknown Artist"
            album = meta.get("album", ["Unknown Album"])[0] if meta else "Unknown Album"
            genre = meta.get("genre", ["Unknown"])[0] if meta else "Unknown"

            # 2. Deep Audio Analysis (Librosa)
            # Load audio (downsample to 22050Hz mono for speed)
            y, sr = librosa.load(file_path, sr=22050, mono=True)

            # Extract BPM (Tempo)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            bpm = float(tempo)

            # Extract Key (Chroma)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key_idx = np.argmax(np.mean(chroma, axis=1))
            keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            musical_key = keys[key_idx]

            # Extract Energy/Loudness (RMS)
            rms = librosa.feature.rms(y=y)
            loudness = float(np.mean(rms))

            # Danceability (Pulse clarity placeholder)
            # Higher variance in onset strength usually implies stronger rhythmic pulse
            danceability = float(np.std(onset_env))

            # Duration
            duration = librosa.get_duration(y=y, sr=sr)

            fingerprint = SonicFingerprint(
                bpm=round(bpm, 1),
                duration=round(duration, 2),
                key=musical_key,
                energy=round(loudness, 4),
                danceability=round(danceability, 4),
                loudness=round(loudness, 4),  # Redundant but explicit
            )

            logger.info(f"Analysis complete: {title} ({bpm} BPM, Key: {musical_key})")

            return {
                "id": filename,  # ID is filename for local files
                "filename": filename,
                "title": title,
                "artist": artist,
                "album": album,
                "genre": genre,
                "fingerprint": fingerprint.to_dict(),
                "ingested_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Deep analysis failed for {filename}: {e}")
            # Fallback for when Librosa fails (e.g. ffmpeg missing or wrong format)
            # Return basic info so file is still usable
            return {
                "id": filename,
                "filename": filename,
                "title": os.path.splitext(filename)[0],
                "artist": "Unknown (Analysis Failed)",
                "genre": "Unknown",
                "fingerprint": {},
                "error": str(e),
            }

    def scan_directory(self) -> list[dict[str, Any]]:
        """Scan entire library directory."""
        results = []
        supported_ext = {".wav", ".mp3", ".ogg", ".flac"}

        for file in os.listdir(self.library_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_ext:
                # TODO: Check if already analyzed to skip re-processing
                result = self.scan_file(file)
                if result:
                    results.append(result)
        return results
