"""Tests for streaming.audio_tools and legacy datasets.dataset."""

import wave

from qfzz.datasets.dataset import Dataset, DatasetLicense
from qfzz.streaming.audio_tools import generate_tone


class TestStreamingAudioTools:
    def test_generate_tone_writes_valid_wav(self, tmp_path):
        out = tmp_path / "tone.wav"
        assert generate_tone(str(out), duration_sec=1, freq_hz=440) is True
        assert out.exists() and out.stat().st_size > 100
        with wave.open(str(out), "r") as wav:
            assert wav.getnchannels() == 1
            assert wav.getframerate() == 44100
            assert wav.getnframes() == 44100

    def test_generate_tone_returns_false_on_oserror(self, tmp_path, monkeypatch):
        out = tmp_path / "blocked.wav"

        def boom(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr("qfzz.streaming.audio_tools.wave.open", boom)
        assert generate_tone(str(out), duration_sec=1, freq_hz=440) is False


class TestLegacyDatasetModule:
    def test_license_enum_values(self):
        assert DatasetLicense.MIT.value == "MIT"
        assert DatasetLicense.PUBLIC_DOMAIN.value == "Public Domain"
        assert DatasetLicense.CC_BY_SA.value == "CC-BY-SA"

    def test_dataset_defaults(self):
        ds = Dataset(
            id="ds1",
            name="Open Beats",
            description="CC music",
            license=DatasetLicense.CC_BY,
            source_url="https://example.com/ds",
            quality_score=0.9,
            category="music",
            size_mb=12.5,
        )
        assert ds.downloads == 0
        assert ds.community_rating == 0.0
        assert ds.verified is False
        assert ds.created_at is not None
        assert ds.license == DatasetLicense.CC_BY
