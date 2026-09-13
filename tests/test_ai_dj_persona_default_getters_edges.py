"""AIDJ persona getters fall back when persona_config omits name/description."""

from qfzz.dj.ai_dj import AIDJ


def test_persona_name_description_defaults_when_keys_missing():
    dj = AIDJ.__new__(AIDJ)
    dj.persona_config = {"style": "friendly"}
    assert dj.get_persona_name() == "DJ"
    assert dj.get_persona_description() == ""
