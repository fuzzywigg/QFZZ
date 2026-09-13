"""Edge coverage for ContentScanner mutagen=None metadata and directory filters."""

from unittest.mock import MagicMock, patch

import numpy as np

from qfzz.library.scanner import ContentScanner


def _librosa_patches(y=None, chroma=None, rms=None, onset=None):
    y = y if y is not None else np.zeros(22050, dtype=np.float32)
    chroma = chroma if chroma is not None else np.zeros((12, 10), dtype=np.float32)
    chroma[0, :] = 1.0
    rms = rms if rms is not None else np.array([[0.1, 0.2]])
    onset = onset if onset is not None else np.array([0.1, 0.2])
    return [
        patch("qfzz.library.scanner.librosa.load", return_value=(y, 22050)),
        patch("qfzz.library.scanner.librosa.onset.onset_strength", return_value=onset),
        patch("qfzz.library.scanner.librosa.beat.beat_track", return_value=(100.0, None)),
        patch("qfzz.library.scanner.librosa.feature.chroma_cqt", return_value=chroma),
        patch("qfzz.library.scanner.librosa.feature.rms", return_value=rms),
        patch("qfzz.library.scanner.librosa.get_duration", return_value=30.0),
    ]


def test_mutagen_none_uses_stem_and_unknown_artist(tmp_path):
    audio = tmp_path / "lonely_song.ogg"
    audio.write_bytes(b"fake-ogg")
    patches = [patch("qfzz.library.scanner.mutagen.File", return_value=None), *_librosa_patches()]
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        scanner = ContentScanner(str(tmp_path))
        result = scanner.scan_file("lonely_song.ogg")
    assert result is not None
    assert result["title"] == "lonely_song"
    assert result["artist"] == "Unknown Artist"


def test_empty_tag_lists_hit_indexerror_fallback(tmp_path):
    """Empty mutagen tag lists raise IndexError on [0]; scanner returns analysis-failed stub."""
    audio = tmp_path / "t.mp3"
    audio.write_bytes(b"fake")
    meta = MagicMock()
    meta.get.side_effect = lambda key, default=None: {
        "title": [],
        "artist": [],
        "album": [],
        "genre": [],
    }.get(key, default)
    patches = [patch("qfzz.library.scanner.mutagen.File", return_value=meta), *_librosa_patches()]
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        scanner = ContentScanner(str(tmp_path))
        result = scanner.scan_file("t.mp3")
    assert result is not None
    assert result["title"] == "t"
    assert "Analysis Failed" in result["artist"]
    assert "error" in result


def test_scan_directory_includes_ogg_skips_unsupported(tmp_path):
    (tmp_path / "a.ogg").write_bytes(b"o")
    (tmp_path / "b.txt").write_bytes(b"t")
    (tmp_path / "c.flac").write_bytes(b"f")

    def fake_scan(filename):
        return {"filename": filename, "title": filename}

    scanner = ContentScanner(str(tmp_path))
    with patch.object(scanner, "scan_file", side_effect=fake_scan):
        results = scanner.scan_directory()
    names = {r["filename"] for r in results}
    assert "a.ogg" in names
    assert "c.flac" in names
    assert "b.txt" not in names
