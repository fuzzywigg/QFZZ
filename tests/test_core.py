"""Test suite for QFZZ core station orchestration."""

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
