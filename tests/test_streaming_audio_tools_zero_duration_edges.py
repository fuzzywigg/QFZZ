"""streaming.audio_tools.generate_tone duration_sec=0 parity with audio.generator."""

import wave

from qfzz.streaming.audio_tools import generate_tone


def test_streaming_generate_tone_zero_duration(tmp_path):
    out = tmp_path / "empty_stream.wav"
    assert generate_tone(str(out), duration_sec=0, freq_hz=220) is True
    with wave.open(str(out), "r") as wav:
        assert wav.getnframes() == 0
