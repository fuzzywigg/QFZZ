"""QFZZStation logs quantum-available branch when provider reports available."""

from unittest.mock import MagicMock, patch

from qfzz import QFZZStation, StationConfig


def test_quantum_available_provider_is_wired():
    config = StationConfig(
        station_id="q-avail",
        station_name="Quantum Up",
        enable_quantum=True,
        enable_edge_optimization=False,
        enable_blockchain=False,
    )
    fake_qp = MagicMock()
    fake_qp.is_available = True

    with (
        patch("qfzz.streaming.player.MusicPlayer") as mock_player,
        patch("qfzz.quantum.provider.QuantumProvider", return_value=fake_qp),
    ):
        mock_player.return_value = MagicMock()
        station = QFZZStation(config)
        station.start()
        try:
            assert station._quantum_provider is fake_qp
            assert station._quantum_provider.is_available is True
            assert station.get_station_stats()["quantum_enabled"] is True
        finally:
            station.stop()
