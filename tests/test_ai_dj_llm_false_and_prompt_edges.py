"""AIDJ success=False fallbacks, empty-track prompts, banned-memory merge."""

from unittest.mock import MagicMock, patch

from qfzz.core.llm_router import LLMResponse
from qfzz.dj.ai_dj import AIDJ


def _fail_response():
    return LLMResponse(
        content="",
        provider="x",
        model="y",
        cost=0.0,
        latency=0.0,
        success=False,
        error="nope",
    )


def test_respond_success_false_uses_fallback():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.return_value = _fail_response()
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        text = dj.respond_to_listener("play ambient")
    assert "Thanks for tuning in" in text


def test_transition_success_false_uses_fallback():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.return_value = _fail_response()
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        text = dj.generate_transition({"title": "Old"}, {"title": "Neon Drift"})
    assert "And now" in text
    assert "Neon Drift" in text


def test_station_id_exception_uses_fallback():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.side_effect = RuntimeError("router dead")
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        assert dj.generate_station_id() == "You're listening to QFZZ FuzzyRadio!"


def test_fallback_intro_missing_track_keys():
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        dj = AIDJ(personas_config_path="config/dj-personas.json")
    text = dj._get_fallback_intro({})
    assert "this track" in text
    assert "Unknown Artist" in text


def test_build_intro_prompt_defaults_and_personas():
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        energetic = AIDJ(persona="energetic", personas_config_path="config/dj-personas.json")
        prompt = energetic._build_intro_prompt({})
    assert "Unknown Track" in prompt
    assert "Unknown Artist" in prompt
    assert "Electronic" in prompt
    assert "pumped" in prompt.lower() or "energetic" in prompt.lower()

    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        story = AIDJ(persona="storyteller", personas_config_path="config/dj-personas.json")
        story_prompt = story._build_intro_prompt({"title": "T", "artist": "A", "genre": "Jazz"})
    assert "stories" in story_prompt.lower() or "storyteller" in story_prompt.lower()

    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        intel = AIDJ(persona="intellectual", personas_config_path="config/dj-personas.json")
        intel_prompt = intel._build_intro_prompt({"title": "T", "artist": "A"})
    assert "educates" in intel_prompt.lower() or "knowledgeable" in intel_prompt.lower()


def test_filter_banned_merges_dj_memory_phrases():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter"),
        patch("qfzz.dj.ai_dj.StateManager") as mock_state,
    ):
        state = MagicMock()
        state.get_dj_memory.return_value = {"banned_phrases": ["secret-token"]}
        mock_state.return_value = state
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        filtered = dj._filter_banned_phrases("AI and secret-token music")
    assert "AI" not in filtered
    assert "secret-token" not in filtered
    assert "music" in filtered
