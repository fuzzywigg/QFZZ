"""Test suite for QFZZ core functionality"""

import pytest
from qfzz import QFZZStation, StationConfig


def test_station_initialization():
    """Test basic station initialization"""
    config = StationConfig(station_name="Test Station")
    station = QFZZStation(config)
    assert station.config.station_name == "Test Station"
    assert station.is_running == False


def test_station_start_stop():
    """Test station start and stop"""
    station = QFZZStation()
    station.start()
    assert station.is_running == True
    
    station.stop()
    assert station.is_running == False


def test_station_status():
    """Test station status retrieval"""
    config = StationConfig(edge_mode=True, blockchain_enabled=True)
    station = QFZZStation(config)
    station.initialize()
    
    status = station.get_status()
    assert status['name'] == "QFZZ"
    assert status['edge_mode'] == True
    assert status['blockchain_enabled'] == True
