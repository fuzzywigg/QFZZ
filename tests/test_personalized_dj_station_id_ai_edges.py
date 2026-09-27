"""PersonalizedDJ.generate_station_id delegates to AI DJ when wired."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_generate_station_id_delegates_to_ai_dj():
    with (
        patch("qfzz.dj.personalized_dj.LLMRouter"),
        patch("qfzz.dj.personalized_dj.QFZZKnowledgeGraph"),
        patch("qfzz.dj.personalized_dj.SovereignLedger"),
        patch("qfzz.dj.personalized_dj.ContentScanner"),
        patch("qfzz.dj.personalized_dj.ContentFetcher"),
        patch("qfzz.dj.personalized_dj.AIDJ") as aidj_cls,
    ):
        aidj = MagicMock()
        aidj.get_persona_name.return_value = "Energetic"
        aidj.generate_station_id.return_value = "This is QFZZ — stay fuzzy."
        aidj_cls.return_value = aidj

        dj = PersonalizedDJ(enable_ai_dj=True)
        assert dj.ai_dj is aidj
        assert dj.generate_station_id() == "This is QFZZ — stay fuzzy."
        aidj.generate_station_id.assert_called_once()
