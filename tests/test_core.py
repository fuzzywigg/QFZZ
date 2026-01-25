"""Test suite for QFZZ core functionality"""

import pytest
from qfzz import QFZZStation, StationConfig


def test_station_initialization():
    """Test basic station initialization"""
    config = StationConfig(station_name="Test Station")
    station = QFZZStation(config)
    assert station.config.station_name == "Test Station"
    assert not station.is_running


def test_station_start_stop():
    """Test station start and stop"""
    station = QFZZStation()
    station.start()
    assert station.is_running
    
    station.stop()
    assert not station.is_running


def test_station_status():
    """Test station status retrieval"""
    config = StationConfig(edge_mode=True, blockchain_enabled=True)
    station = QFZZStation(config)
    station.initialize()
    
    status = station.get_status()
    assert status['name'] == "QFZZ"
    assert status['edge_mode']
    assert status['blockchain_enabled']
