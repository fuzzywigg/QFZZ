"""AIDJ missing personas config file falls back to built-in defaults."""

from unittest.mock import patch

from qfzz.dj.ai_dj import AIDJ


def test_missing_personas_config_uses_default_energetic_and_chill(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        dj = AIDJ(persona="chill", personas_config_path=str(missing))

    assert dj.persona == "chill"
    assert dj.persona_config["name"] == "Smooth Vibes"
    assert set(dj.get_available_personas()) >= {"energetic", "chill"}
