"""PersonalizedDJ AIDJ constructor soft-clear on init failures."""

from unittest.mock import patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_aidj_import_error_clears_ai_dj():
    with patch("qfzz.dj.personalized_dj.AIDJ", side_effect=ImportError("no aidj")):
        dj = PersonalizedDJ(enable_ai_dj=True)
        assert dj.ai_dj is None
        assert dj.get_ai_dj_persona() is None
        assert "FuzzyRadio" in dj.generate_station_id()


def test_aidj_file_not_found_clears_ai_dj():
    with patch(
        "qfzz.dj.personalized_dj.AIDJ",
        side_effect=FileNotFoundError("persona.json"),
    ):
        dj = PersonalizedDJ(enable_ai_dj=True)
        assert dj.ai_dj is None


def test_aidj_generic_exception_clears_ai_dj():
    with patch(
        "qfzz.dj.personalized_dj.AIDJ",
        side_effect=RuntimeError("boom"),
    ):
        dj = PersonalizedDJ(enable_ai_dj=True)
        assert dj.ai_dj is None


def test_set_ai_dj_persona_failure_returns_false():
    dj = PersonalizedDJ(enable_ai_dj=False)
    with patch("qfzz.dj.personalized_dj.AIDJ", side_effect=ValueError("bad")):
        assert dj.set_ai_dj_persona("energetic") is False
