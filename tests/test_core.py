"""Test suite for QFZZ core functionality"""

from qfzz import QFZZStation, StationConfig


def test_station_initialization():
    """Test basic station initialization"""
    config = StationConfig(station_id="test-station", station_name="Test Station")
    station = QFZZStation(config)
    assert station.config.station_name == "Test Station"
    assert station.is_running() is False


def test_station_start_stop():
    """Test station start and stop"""
    config = StationConfig(station_id="test-station", station_name="Test Station")
    station = QFZZStation(config)
    station.start()
    assert station.is_running() is True

    station.stop()
    assert station.is_running() is False


def test_station_status():
    """Test station status retrieval"""
    config = StationConfig(
        station_id="qfzz",
        station_name="QFZZ",
        enable_edge_optimization=True,
        enable_blockchain=True,
    )
    station = QFZZStation(config)

    status = station.get_station_stats()
    assert status["station_name"] == "QFZZ"
    assert status["edge_optimization_enabled"] is True
    assert status["blockchain_enabled"] is True
