"""Extra generate_tone edge cases beyond the base suite."""

from pathlib import Path

from qfzz.streaming.audio_tools import generate_tone


def test_generate_tone_short_duration_and_high_freq(tmp_path: Path):
    out = tmp_path / "short.wav"
    assert generate_tone(str(out), duration_sec=1, freq_hz=880) is True
    assert out.exists()
    assert out.stat().st_size > 44


def test_generate_tone_zero_duration_still_creates_header(tmp_path: Path):
    out = tmp_path / "emptyish.wav"
    assert generate_tone(str(out), duration_sec=0, freq_hz=440) is True
    assert out.exists()
