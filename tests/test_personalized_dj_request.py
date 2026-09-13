"""Additional PersonalizedDJ coverage: request_track, interact, segue (mocked deps)."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def _make_dj(**kwargs):
    """Construct PersonalizedDJ without heavy side effects from real LLM/KG paths."""
    with patch("qfzz.dj.personalized_dj.QFZZKnowledgeGraph") as kg_cls:
        with patch("qfzz.dj.personalized_dj.ContentScanner"):
            with patch("qfzz.dj.personalized_dj.SovereignLedger") as ledger_cls:
                with patch("qfzz.dj.personalized_dj.ContentFetcher") as fetcher_cls:
                    with patch("qfzz.dj.personalized_dj.LLMRouter") as router_cls:
                        with patch("qfzz.dj.personalized_dj.AIDJ") as ai_cls:
                            kg = MagicMock()
                            kg_cls.return_value = kg
                            ledger = MagicMock()
                            ledger_cls.return_value = ledger
                            fetcher = MagicMock()
                            fetcher_cls.return_value = fetcher
                            router = MagicMock()
                            router.get_available_providers.return_value = ["Mock"]
                            router_cls.return_value = router
                            ai = MagicMock()
                            ai.get_persona_name.return_value = "Energetic"
                            ai_cls.return_value = ai
                            dj = PersonalizedDJ(enable_ai_dj=kwargs.pop("enable_ai_dj", True), **kwargs)
                            dj._test_kg = kg
                            dj._test_ledger = ledger
                            dj._test_fetcher = fetcher
                            dj._test_router = router
                            dj._test_ai = ai
                            return dj


class TestPersonalizedDJRequestAndInteract:
    def test_request_track_success_registers_kg_and_ledger(self):
        dj = _make_dj()
        track = {
            "title": "Orbit",
            "artist": "Nova",
            "filename": "orbit.mp3",
            "genre": "External",
        }
        dj._test_fetcher.fetch_from_url.return_value = track
        result = dj.request_track("https://archive.org/details/orbit")
        assert result == track
        dj._test_kg.add_track_node.assert_called_once_with("orbit.mp3", track)
        dj._test_ledger.record_event.assert_called_once()

    def test_request_track_failure_returns_none(self):
        dj = _make_dj()
        dj._test_fetcher.fetch_from_url.return_value = None
        assert dj.request_track("https://bad.example/x") is None
        dj._test_kg.add_track_node.assert_not_called()

    def test_interact_uses_ai_dj_when_available(self):
        dj = _make_dj()
        dj._test_ai.respond_to_listener.return_value = "spinning jazz"
        assert dj.interact("u1", "play jazz") == "spinning jazz"
        dj._test_ai.respond_to_listener.assert_called_once_with("play jazz")

    def test_interact_falls_back_to_router_without_ai(self):
        dj = _make_dj(enable_ai_dj=False)
        dj.ai_dj = None
        dj._test_router.generate.return_value = {"text": "router reply"}
        assert dj.interact("u2", "hello") == "router reply"
        dj._test_router.generate.assert_called_once()

    def test_generate_segue_with_ai(self):
        dj = _make_dj()
        next_track = {"title": "Next", "artist": "A"}
        dj._test_ai.introduce_track.return_value = "first up"
        assert dj.generate_segue(None, next_track) == "first up"

        prev = {"title": "Prev", "artist": "A"}
        dj._test_ai.generate_transition.return_value = "and now"
        assert dj.generate_segue(prev, next_track) == "and now"

    def test_generate_segue_without_ai_uses_router(self):
        dj = _make_dj(enable_ai_dj=False)
        dj.ai_dj = None
        dj._test_router.generate.return_value = {"text": "segue text"}
        text = dj.generate_segue(
            {"title": "A", "artist": "Same", "genre": "jazz"},
            {"title": "B", "artist": "Same", "genre": "jazz"},
        )
        assert text == "segue text"
        prompt = dj._test_router.generate.call_args[0][0]
        assert "same artist" in prompt.lower() or "A" in prompt
