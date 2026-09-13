"""AIDJ error/fallback edges: corrupt personas, TTS failures, LLM exceptions."""

from unittest.mock import MagicMock, patch

from qfzz.core.llm_router import LLMResponse
from qfzz.dj.ai_dj import AIDJ


def test_corrupt_personas_json_uses_defaults(tmp_path):
    bad = tmp_path / "personas.json"
    bad.write_text("{not-json", encoding="utf-8")
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        dj = AIDJ(persona="energetic", personas_config_path=str(bad))
    assert dj.persona == "energetic"
    assert dj.persona_config["name"] == "Fuzzy Beats"
    assert "chill" in dj.get_available_personas()


def test_tts_unavailable_clears_client():
    fake = MagicMock()
    fake.is_available.return_value = False
    with (
        patch("qfzz.dj.ai_dj.LLMRouter"),
        patch("qfzz.dj.ai_dj.StateManager"),
        patch("qfzz.dj.ai_dj.TTSClient", return_value=fake),
    ):
        dj = AIDJ(enable_tts=True, personas_config_path="config/dj-personas.json")
    assert dj.tts_client is None


def test_tts_init_exception_clears_client():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter"),
        patch("qfzz.dj.ai_dj.StateManager"),
        patch("qfzz.dj.ai_dj.TTSClient", side_effect=RuntimeError("tts boom")),
    ):
        dj = AIDJ(enable_tts=True, personas_config_path="config/dj-personas.json")
    assert dj.tts_client is None


def test_synthesize_speech_exception_returns_none():
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        dj = AIDJ(enable_tts=False, personas_config_path="config/dj-personas.json")
    assert dj.synthesize_speech("hi") is None

    client = MagicMock()
    client.synthesize.side_effect = RuntimeError("synth fail")
    dj.tts_client = client
    assert dj.synthesize_speech("hi") is None


def test_introduce_raises_uses_fallback():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.side_effect = RuntimeError("boom")
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        text = dj.introduce_track({"title": "T", "artist": "A"})
    assert "Coming up next" in text
    assert "T" in text


def test_respond_and_transition_fallbacks_on_exception():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.side_effect = RuntimeError("boom")
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        assert "Thanks for tuning in" in dj.respond_to_listener("play something")
        assert "And now" in dj.generate_transition(
            {"title": "Old"}, {"title": "New"}
        )


def test_station_id_fallback_on_failure():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.return_value = LLMResponse(
            content="",
            provider="x",
            model="y",
            cost=0,
            latency=0,
            success=False,
            error="fail",
        )
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        assert dj.generate_station_id() == "You're listening to QFZZ FuzzyRadio!"


def test_filter_banned_survives_dj_memory_error():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter"),
        patch("qfzz.dj.ai_dj.StateManager") as mock_state,
    ):
        state = MagicMock()
        state.get_dj_memory.side_effect = RuntimeError("memory down")
        mock_state.return_value = state
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        filtered = dj._filter_banned_phrases("This AI track is generated")
    assert "AI" not in filtered
    assert "generated" not in filtered.lower() or "generated" not in filtered
