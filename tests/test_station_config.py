"""Tests for StationConfig validation and serialization."""

import json

import pytest

from qfzz.core.config import StationConfig


def test_valid_config_roundtrip():
    config = StationConfig(station_id="s1", station_name="Alpha")
    data = config.to_dict()
    restored = StationConfig.from_dict(data)
    assert restored.station_id == "s1"
    assert restored.station_name == "Alpha"
    assert restored.max_playlist_size == 100

    parsed = StationConfig.from_json(config.to_json())
    assert parsed.station_id == "s1"
    assert json.loads(parsed.to_json())["streaming_quality"] == "high"


@pytest.mark.parametrize(
    "kwargs,match",
    [
        ({"station_id": "", "station_name": "x"}, "station_id"),
        ({"station_id": "s", "station_name": ""}, "station_name"),
        ({"station_id": "s", "station_name": "n", "max_playlist_size": 0}, "max_playlist_size"),
        ({"station_id": "s", "station_name": "n", "trust_threshold": 1.5}, "trust_threshold"),
        (
            {"station_id": "s", "station_name": "n", "streaming_quality": "ultra"},
            "streaming_quality",
        ),
        ({"station_id": "s", "station_name": "n", "cache_size_mb": -1}, "cache_size_mb"),
    ],
)
def test_invalid_config_raises(kwargs, match):
    with pytest.raises(ValueError, match=match):
        StationConfig(**kwargs)
