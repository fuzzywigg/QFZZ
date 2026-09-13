"""AIDJ generate_station_id Exception path uses hard-coded fallback."""

from unittest.mock import MagicMock, patch

from qfzz.dj.ai_dj import AIDJ


def test_station_id_exception_uses_fallback_copy():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.side_effect = RuntimeError("router down")
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        assert dj.generate_station_id() == "You're listening to QFZZ FuzzyRadio!"
