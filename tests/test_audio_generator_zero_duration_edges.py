"""generate_tone with duration_sec=0 writes an empty WAV."""

import wave

from qfzz.audio.generator import generate_tone


def test_generate_tone_zero_duration_writes_empty_wav(tmp_path):
    out = tmp_path / "empty.wav"
    assert generate_tone(str(out), duration_sec=0, freq_hz=440) is True
    with wave.open(str(out), "r") as wav:
        assert wav.getnframes() == 0
        assert wav.getframerate() == 44100
