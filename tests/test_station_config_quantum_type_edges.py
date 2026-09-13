"""StationConfig.enable_quantum type validation edge."""

import pytest

from qfzz.core.config import StationConfig


def test_enable_quantum_non_bool_raises():
    with pytest.raises(ValueError, match="enable_quantum must be a boolean"):
        StationConfig(
            station_id="s1",
            station_name="Test",
            enable_quantum="yes",  # type: ignore[arg-type]
        )


def test_enable_quantum_true_accepted():
    cfg = StationConfig(station_id="s1", station_name="Test", enable_quantum=True)
    assert cfg.enable_quantum is True
    assert cfg.to_dict()["enable_quantum"] is True
