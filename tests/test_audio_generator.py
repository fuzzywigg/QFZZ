"""Tests for audio tone generation."""

import wave

from qfzz.audio.generator import generate_tone


def test_generate_tone_writes_valid_wav(tmp_path):
    out = tmp_path / "tone.wav"
    assert generate_tone(str(out), duration_sec=1, freq_hz=440) is True
    assert out.exists() and out.stat().st_size > 100
    with wave.open(str(out), "r") as wav:
        assert wav.getnchannels() == 1
        assert wav.getframerate() == 44100
        assert wav.getnframes() == 44100


def test_generate_tone_returns_false_on_oserror(tmp_path, monkeypatch):
    out = tmp_path / "blocked.wav"

    def boom(*_args, **_kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("qfzz.audio.generator.wave.open", boom)
    assert generate_tone(str(out), duration_sec=1, freq_hz=440) is False
