"""Test suite for QFZZ core station orchestration."""

from unittest.mock import MagicMock

import pytest

from qfzz import QFZZStation, StationConfig


def _config(**overrides) -> StationConfig:
    base = {
        "station_id": "test-station",
        "station_name": "Test Station",
    }
    base.update(overrides)
    return StationConfig(**base)


def test_station_initialization():
    """Station stores config and starts stopped."""
    config = _config(station_name="Test Station")
    station = QFZZStation(config)
    assert station.config.station_name == "Test Station"
    assert station.config.station_id == "test-station"
    assert station.is_running() is False


def test_station_start_stop():
    """Station start/stop toggles running state."""
    station = QFZZStation(_config())
    station.start()
    assert station.is_running() is True

    station.stop()
    assert station.is_running() is False


def test_station_stats():
    """get_station_stats reports config flags and listener count."""
    config = _config(enable_edge_optimization=True, enable_blockchain=True)
    station = QFZZStation(config)
    station.start()

    stats = station.get_station_stats()
    assert stats["station_name"] == "Test Station"
    assert stats["running"] is True
    assert stats["listener_count"] == 0
    assert stats["edge_optimization_enabled"] is True
    assert stats["blockchain_enabled"] is True


def test_add_listener_requires_running_station():
    """Listeners cannot be added while the station is stopped."""
    station = QFZZStation(_config())
    with pytest.raises(RuntimeError, match="not running"):
        station.add_listener("user-1")


def test_listener_playlist_flow():
    """Running station can add a listener and generate a playlist."""
    station = QFZZStation(_config(max_playlist_size=5))
    station.start()
    station.add_listener("user-1", preferences={"genres": {"ambient": 1.0}})

    playlist = station.generate_playlist("user-1")
    assert isinstance(playlist, list)
    assert len(playlist) <= 5

    station.remove_listener("user-1")
    with pytest.raises(ValueError, match="not a listener"):
        station.generate_playlist("user-1")


def test_double_start_and_stop_are_idempotent():
    station = QFZZStation(_config())
    station.start()
    station.start()
    assert station.is_running() is True
    station.stop()
    station.stop()
    assert station.is_running() is False


def test_record_interaction_requires_running_listener():
    station = QFZZStation(_config())
    with pytest.raises(RuntimeError, match="not running"):
        station.record_interaction("user-1", "t1", "like")

    station.start()
    with pytest.raises(ValueError, match="not a listener"):
        station.record_interaction("user-1", "t1", "like")

    station.add_listener("user-1")
    station.record_interaction("user-1", "track_0001", "like", rating=0.9)


def test_generate_playlist_filters_by_trust_when_blockchain_enabled():
    station = QFZZStation(_config(enable_blockchain=True, trust_threshold=0.7, max_playlist_size=10))
    station.start()
    assert station._trust_network is not None

    station._dj.recommend = MagicMock(
        return_value=[
            {"track_id": "hi", "content_id": "c-hi", "creator_id": "u-hi"},
            {"track_id": "lo", "content_id": "c-lo", "creator_id": "u-lo"},
        ]
    )
    station._trust_network.get_trust_score = MagicMock(
        side_effect=lambda content_id, creator_id: 0.9 if content_id == "c-hi" else 0.1
    )
    station.add_listener("user-1")
    playlist = station.generate_playlist("user-1")
    assert [t["track_id"] for t in playlist] == ["hi"]
