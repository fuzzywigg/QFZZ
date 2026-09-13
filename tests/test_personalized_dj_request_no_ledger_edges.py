"""PersonalizedDJ.request_track skips ledger.record_event when ledger is None."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_request_track_without_ledger_still_returns_track():
    with (
        patch("qfzz.dj.personalized_dj.QFZZKnowledgeGraph") as kg_cls,
        patch("qfzz.dj.personalized_dj.ContentScanner"),
        patch("qfzz.dj.personalized_dj.SovereignLedger"),
        patch("qfzz.dj.personalized_dj.ContentFetcher") as fetcher_cls,
        patch("qfzz.dj.personalized_dj.LLMRouter") as router_cls,
    ):
        kg = MagicMock()
        kg_cls.return_value = kg
        fetcher = MagicMock()
        fetcher_cls.return_value = fetcher
        router = MagicMock()
        router.get_available_providers.return_value = ["Mock"]
        router_cls.return_value = router

        dj = PersonalizedDJ(enable_ai_dj=False)
        dj.ledger = None
        track = {
            "title": "Orbit",
            "artist": "Nova",
            "filename": "orbit.mp3",
            "genre": "External",
        }
        fetcher.fetch_from_url.return_value = track

        result = dj.request_track("https://archive.org/details/orbit")

    assert result == track
    kg.add_track_node.assert_called_once_with("orbit.mp3", track)
