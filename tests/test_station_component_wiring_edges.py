"""QFZZStation component wiring: quantum/edge/blockchain + cleanup + stats flags."""

from unittest.mock import MagicMock, patch

from qfzz import QFZZStation, StationConfig


def test_enable_flags_wire_components_and_stats():
    config = StationConfig(
        station_id="wire",
        station_name="Wire Station",
        enable_quantum=True,
        enable_edge_optimization=True,
        enable_blockchain=True,
    )
    with patch("qfzz.streaming.player.MusicPlayer") as mock_player:
        mock_player.return_value = MagicMock()
        station = QFZZStation(config)
        station.start()
        try:
            assert station._quantum_provider is not None
            assert station._edge_optimizer is not None
            assert station._trust_network is not None
            assert station._dj is not None
            assert station._player is not None
            stats = station.get_station_stats()
            assert stats["quantum_enabled"] is True
            assert stats["edge_optimization_enabled"] is True
            assert stats["blockchain_enabled"] is True
            assert stats["running"] is True
        finally:
            station.stop()
            assert station._dj is None
            assert station._player is None
            assert station._quantum_provider is None
            assert station._edge_optimizer is None
            assert station._trust_network is None
            assert station._dataset_manager is None


def test_disabled_flags_leave_optional_components_none():
    config = StationConfig(
        station_id="plain",
        station_name="Plain",
        enable_quantum=False,
        enable_edge_optimization=False,
        enable_blockchain=False,
    )
    with patch("qfzz.streaming.player.MusicPlayer") as mock_player:
        mock_player.return_value = MagicMock()
        station = QFZZStation(config)
        station.start()
        try:
            assert station._quantum_provider is None
            assert station._edge_optimizer is None
            assert station._trust_network is None
            stats = station.get_station_stats()
            assert stats["quantum_enabled"] is False
            assert stats["blockchain_enabled"] is False
        finally:
            station.stop()
