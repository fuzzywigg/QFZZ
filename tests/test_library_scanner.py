"""Tests for qfzz.library.scanner ContentScanner and SonicFingerprint."""

from unittest.mock import MagicMock, patch

import numpy as np

from qfzz.library.scanner import ContentScanner, SonicFingerprint


class TestSonicFingerprint:
    def test_to_dict(self):
        fp = SonicFingerprint(
            bpm=120.0,
            duration=180.5,
            key="Am",
            energy=0.4,
            danceability=0.6,
            loudness=0.4,
        )
        data = fp.to_dict()
        assert data["bpm"] == 120.0
        assert data["key"] == "Am"
        assert set(data) == {
            "bpm",
            "duration",
            "key",
            "energy",
            "danceability",
            "loudness",
        }


class TestContentScanner:
    def test_missing_file_returns_none(self, tmp_path):
        scanner = ContentScanner(str(tmp_path))
        assert scanner.scan_file("missing.mp3") is None

    def test_scan_file_happy_path(self, tmp_path):
        audio = tmp_path / "track.wav"
        audio.write_bytes(b"fake-wav")

        meta = MagicMock()
        meta.get.side_effect = lambda key, default=None: {
            "title": ["Cosmic Drift"],
            "artist": ["Nova"],
            "album": ["Space"],
            "genre": ["Ambient"],
        }.get(key, default)

        y = np.zeros(22050, dtype=np.float32)
        chroma = np.zeros((12, 10), dtype=np.float32)
        chroma[9, :] = 1.0  # A
        rms = np.array([[0.2, 0.3]])
        onset = np.array([0.1, 0.5, 0.2])

        with patch("qfzz.library.scanner.mutagen.File", return_value=meta):
            with patch("qfzz.library.scanner.librosa.load", return_value=(y, 22050)):
                with patch(
                    "qfzz.library.scanner.librosa.onset.onset_strength", return_value=onset
                ):
                    with patch(
                        "qfzz.library.scanner.librosa.beat.beat_track",
                        return_value=(128.4, None),
                    ):
                        with patch(
                            "qfzz.library.scanner.librosa.feature.chroma_cqt",
                            return_value=chroma,
                        ):
                            with patch(
                                "qfzz.library.scanner.librosa.feature.rms", return_value=rms
                            ):
                                with patch(
                                    "qfzz.library.scanner.librosa.get_duration",
                                    return_value=42.25,
                                ):
                                    scanner = ContentScanner(str(tmp_path))
                                    result = scanner.scan_file("track.wav")

        assert result is not None
        assert result["title"] == "Cosmic Drift"
        assert result["artist"] == "Nova"
        assert result["album"] == "Space"
        assert result["genre"] == "Ambient"
        assert result["fingerprint"]["bpm"] == 128.4
        assert result["fingerprint"]["key"] == "A"
        assert result["fingerprint"]["duration"] == 42.25
        assert "ingested_at" in result

    def test_scan_file_fallback_on_librosa_error(self, tmp_path):
        audio = tmp_path / "broken.mp3"
        audio.write_bytes(b"nope")

        with patch("qfzz.library.scanner.mutagen.File", side_effect=RuntimeError("bad audio")):
            scanner = ContentScanner(str(tmp_path))
            result = scanner.scan_file("broken.mp3")

        assert result is not None
        assert result["filename"] == "broken.mp3"
        assert result["artist"] == "Unknown (Analysis Failed)"
        assert result["fingerprint"] == {}
        assert "error" in result

    def test_scan_directory_filters_extensions(self, tmp_path):
        (tmp_path / "a.wav").write_bytes(b"a")
        (tmp_path / "b.mp3").write_bytes(b"b")
        (tmp_path / "c.txt").write_bytes(b"c")
        (tmp_path / "d.flac").write_bytes(b"d")

        scanner = ContentScanner(str(tmp_path))
        with patch.object(
            scanner,
            "scan_file",
            side_effect=lambda name: {"filename": name},
        ) as scan_file:
            results = scanner.scan_directory()

        scanned = {r["filename"] for r in results}
        assert scanned == {"a.wav", "b.mp3", "d.flac"}
        assert scan_file.call_count == 3

    def test_scan_directory_skips_none_results(self, tmp_path):
        (tmp_path / "gone.ogg").write_bytes(b"x")
        scanner = ContentScanner(str(tmp_path))
        with patch.object(scanner, "scan_file", return_value=None):
            assert scanner.scan_directory() == []
