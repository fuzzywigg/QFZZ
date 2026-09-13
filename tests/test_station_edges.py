"""Edge-path coverage for QFZZStation orchestration."""

from unittest.mock import MagicMock

import pytest

from qfzz import QFZZStation, StationConfig


def _config(**overrides) -> StationConfig:
    base = {
        "station_id": "edge-station",
        "station_name": "Edge Station",
        "max_playlist_size": 3,
        "trust_threshold": 0.7,
    }
    base.update(overrides)
    return StationConfig(**base)


def test_start_stop_idempotent():
    station = QFZZStation(_config())
    station.start()
    assert station.is_running() is True
    station.start()  # already running → no-op
    assert station.is_running() is True

    station.stop()
    assert station.is_running() is False
    station.stop()  # already stopped → no-op
    assert station.is_running() is False


def test_generate_playlist_and_interaction_require_running():
    station = QFZZStation(_config())
    with pytest.raises(RuntimeError, match="not running"):
        station.generate_playlist("u1")
    with pytest.raises(RuntimeError, match="not running"):
        station.record_interaction("u1", "t1", "like")


def test_remove_listener_missing_is_noop():
    station = QFZZStation(_config())
    station.start()
    station.remove_listener("ghost")  # should not raise
    station.stop()


def test_record_interaction_unknown_listener():
    station = QFZZStation(_config())
    station.start()
    with pytest.raises(ValueError, match="not a listener"):
        station.record_interaction("nobody", "t1", "like")
    station.stop()


def test_record_interaction_delegates_to_dj():
    station = QFZZStation(_config())
    station.start()
    station.add_listener("u1")
    station._dj = MagicMock()
    station.record_interaction("u1", "track-9", "like", rating=0.9)
    station._dj.record_feedback.assert_called_once_with("u1", "track-9", "like", 0.9)
    station.stop()


def test_trust_filter_drops_low_score_tracks():
    station = QFZZStation(_config(enable_blockchain=True, trust_threshold=0.8))
    station.start()
    station.add_listener("u1", preferences={"genres": {"ambient": 1.0}})

    station._dj = MagicMock()
    station._dj.recommend.return_value = [
        {"track_id": "hi", "content_id": "c-hi", "creator_id": "cr", "title": "Hi"},
        {"track_id": "lo", "content_id": "c-lo", "creator_id": "cr", "title": "Lo"},
    ]
    station._trust_network = MagicMock()
    station._trust_network.get_trust_score.side_effect = lambda cid, cr: {
        "c-hi": 0.95,
        "c-lo": 0.1,
    }.get(cid, 0.5)

    playlist = station.generate_playlist("u1")
    assert len(playlist) == 1
    assert playlist[0]["track_id"] == "hi"
    station.stop()


def test_playlist_respects_max_size():
    station = QFZZStation(_config(max_playlist_size=2))
    station.start()
    station.add_listener("u1")
    station._dj = MagicMock()
    station._dj.recommend.return_value = [
        {"track_id": f"t{i}", "content_id": f"c{i}", "creator_id": "cr"} for i in range(5)
    ]
    station._trust_network = None
    playlist = station.generate_playlist("u1")
    assert len(playlist) == 2
    assert station._listeners["u1"]["playlist"] == playlist
    station.stop()
