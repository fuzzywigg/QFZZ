"""StationConfig inclusive boundary and serde error edges."""

import json

import pytest

from qfzz.core.config import StationConfig


def test_inclusive_trust_and_cache_and_playlist_bounds():
    cfg = StationConfig(
        station_id="s1",
        station_name="Bounds",
        trust_threshold=0.0,
        cache_size_mb=0,
        max_playlist_size=1,
        streaming_quality="low",
    )
    assert cfg.trust_threshold == 0.0
    assert cfg.cache_size_mb == 0
    assert cfg.max_playlist_size == 1

    cfg2 = StationConfig(
        station_id="s2",
        station_name="Lossless",
        trust_threshold=1.0,
        streaming_quality="lossless",
    )
    assert cfg2.trust_threshold == 1.0
    assert cfg2.streaming_quality == "lossless"


def test_from_json_invalid_raises_json_decode_error():
    with pytest.raises(json.JSONDecodeError):
        StationConfig.from_json("{")


def test_from_dict_unexpected_key_raises_type_error():
    with pytest.raises(TypeError):
        StationConfig.from_dict(
            {"station_id": "s", "station_name": "n", "unknown_field": True}
        )
