"""Audio generator frequency / short-duration edge cases."""

import wave

from qfzz.audio.generator import generate_tone


def test_generate_tone_zero_freq_still_writes_wav(tmp_path):
    out = tmp_path / "zero.wav"
    assert generate_tone(str(out), duration_sec=1, freq_hz=0) is True
    with wave.open(str(out), "r") as wav:
        assert wav.getnframes() == 44100


def test_generate_tone_short_duration(tmp_path):
    out = tmp_path / "short.wav"
    assert generate_tone(str(out), duration_sec=0.1, freq_hz=880) is True
    with wave.open(str(out), "r") as wav:
        assert wav.getnframes() == 4410
        assert wav.getframerate() == 44100
