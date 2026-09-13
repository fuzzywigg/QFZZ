"""ContentScanner meta=None / empty-tag / ogg directory edges."""

from unittest.mock import MagicMock, patch

import numpy as np

from qfzz.library.scanner import ContentScanner


def _librosa_stack():
    y = np.zeros(22050, dtype=np.float32)
    chroma = np.zeros((12, 10), dtype=np.float32)
    chroma[0, :] = 1.0
    rms = np.array([[0.1]])
    onset = np.array([0.2, 0.3])
    return (
        patch("qfzz.library.scanner.librosa.load", return_value=(y, 22050)),
        patch("qfzz.library.scanner.librosa.onset.onset_strength", return_value=onset),
        patch("qfzz.library.scanner.librosa.beat.beat_track", return_value=(100.0, None)),
        patch("qfzz.library.scanner.librosa.feature.chroma_cqt", return_value=chroma),
        patch("qfzz.library.scanner.librosa.feature.rms", return_value=rms),
        patch("qfzz.library.scanner.librosa.get_duration", return_value=10.0),
    )


def test_scan_file_meta_none_uses_filename_defaults(tmp_path):
    (tmp_path / "lonely.wav").write_bytes(b"fake")
    stacks = _librosa_stack()
    with patch("qfzz.library.scanner.mutagen.File", return_value=None):
        with stacks[0], stacks[1], stacks[2], stacks[3], stacks[4], stacks[5]:
            result = ContentScanner(str(tmp_path)).scan_file("lonely.wav")

    assert result is not None
    assert result["title"] == "lonely"
    assert result["artist"] == "Unknown Artist"
    assert result["album"] == "Unknown Album"
    assert result["genre"] == "Unknown"
    assert result["fingerprint"]["key"] == "C"


def test_scan_file_empty_tags_use_defaults(tmp_path):
    (tmp_path / "empty.mp3").write_bytes(b"fake")
    meta = MagicMock()
    meta.get.side_effect = lambda key, default=None: default
    stacks = _librosa_stack()
    with patch("qfzz.library.scanner.mutagen.File", return_value=meta):
        with stacks[0], stacks[1], stacks[2], stacks[3], stacks[4], stacks[5]:
            result = ContentScanner(str(tmp_path)).scan_file("empty.mp3")

    assert result["title"] == "empty"
    assert result["artist"] == "Unknown Artist"
    assert result["album"] == "Unknown Album"


def test_scan_directory_includes_ogg(tmp_path):
    (tmp_path / "a.ogg").write_bytes(b"o")
    (tmp_path / "skip.txt").write_text("nope", encoding="utf-8")
    scanner = ContentScanner(str(tmp_path))
    with patch.object(
        scanner,
        "scan_file",
        side_effect=lambda name: {"id": name, "filename": name} if name.endswith(".ogg") else None,
    ):
        results = scanner.scan_directory()
    assert len(results) == 1
    assert results[0]["filename"] == "a.ogg"
