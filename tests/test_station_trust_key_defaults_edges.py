"""Station listener preference defaults + trust key omissions."""

from unittest.mock import MagicMock

from qfzz import QFZZStation, StationConfig


def _config(**overrides) -> StationConfig:
    base = {
        "station_id": "defaults-station",
        "station_name": "Defaults Station",
        "max_playlist_size": 5,
        "trust_threshold": 0.5,
    }
    base.update(overrides)
    return StationConfig(**base)


def test_add_listener_none_preferences_stored_empty():
    station = QFZZStation(_config())
    station.start()
    station.add_listener("u-none", preferences=None)
    assert station._listeners["u-none"]["preferences"] == {}
    station.stop()


def test_listener_count_in_stats_updates():
    station = QFZZStation(_config())
    station.start()
    assert station.get_station_stats()["listener_count"] == 0
    station.add_listener("a")
    station.add_listener("b")
    assert station.get_station_stats()["listener_count"] == 2
    station.remove_listener("a")
    assert station.get_station_stats()["listener_count"] == 1
    station.stop()


def test_trust_filter_missing_content_creator_ids_uses_empty_keys():
    station = QFZZStation(_config(enable_blockchain=True, trust_threshold=0.8))
    station.start()
    station.add_listener("u1")

    station._dj = MagicMock()
    station._dj.recommend.return_value = [
        {"track_id": "bare", "title": "Bare"},
        {"track_id": "ok", "content_id": "c1", "creator_id": "cr", "title": "Ok"},
    ]
    station._trust_network = MagicMock()

    def score(cid, crid):
        if cid == "" and crid == "":
            return 0.1
        return 0.95

    station._trust_network.get_trust_score.side_effect = score
    playlist = station.generate_playlist("u1")
    ids = [t["track_id"] for t in playlist]
    assert "bare" not in ids
    assert "ok" in ids
    station._trust_network.get_trust_score.assert_any_call("", "")
    station.stop()
