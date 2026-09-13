"""Edge coverage for AIDJ fallbacks, corrupt config, TTS init, and banned-phrase paths."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from qfzz.core.llm_router import LLMResponse
from qfzz.dj.ai_dj import AIDJ


@pytest.fixture
def personas_path(tmp_path: Path) -> str:
    data = {
        "personas": {
            "energetic": {
                "name": "Fuzzy Beats",
                "description": "High-energy DJ",
                "voice_id": "alloy",
                "style": "upbeat",
                "temperature": 0.8,
                "banned_phrases": ["AI", "generated"],
            },
            "storyteller": {
                "name": "Narrator",
                "description": "Story DJ",
                "voice_id": "onyx",
                "style": "narrative",
                "temperature": 0.7,
                "banned_phrases": ["algorithm"],
            },
        }
    }
    path = tmp_path / "personas.json"
    path.write_text(json.dumps(data))
    return str(path)


@pytest.fixture
def dj(personas_path: str):
    with patch("qfzz.dj.ai_dj.LLMRouter") as router_cls:
        with patch("qfzz.dj.ai_dj.StateManager") as state_cls:
            router = MagicMock()
            state = MagicMock()
            state.get_dj_memory.return_value = {
                "banned_phrases": ["language model"],
                "conversation_history": [],
            }
            router_cls.return_value = router
            state_cls.return_value = state
            instance = AIDJ(persona="energetic", personas_config_path=personas_path)
            instance._test_router = router
            instance._test_state = state
            yield instance


def test_corrupt_personas_json_falls_back_to_defaults(tmp_path: Path):
    bad = tmp_path / "broken.json"
    bad.write_text("{not-json")
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        dj = AIDJ(persona="energetic", personas_config_path=str(bad))
    assert "energetic" in dj.get_available_personas()
    assert dj.get_persona_name() == "Fuzzy Beats"


def test_introduce_track_llm_raises_uses_fallback(dj: AIDJ):
    dj._test_router.generate.side_effect = RuntimeError("boom")
    text = dj.introduce_track({"title": "Orbit", "artist": "Nova"})
    assert "Orbit" in text
    assert "Nova" in text


def test_introduce_track_success_false_uses_fallback_missing_keys(dj: AIDJ):
    dj._test_router.generate.return_value = LLMResponse(
        content="",
        provider="mock",
        model="m",
        cost=0.0,
        latency=0.0,
        success=False,
        error="fail",
    )
    text = dj.introduce_track({})
    assert "this track" in text
    assert "Unknown Artist" in text


def test_respond_transition_station_id_fallbacks(dj: AIDJ):
    dj._test_router.generate.side_effect = RuntimeError("down")
    assert "requests" in dj.respond_to_listener("play something").lower()
    assert "next track" in dj.generate_transition({"title": "A"}, {}).lower()
    assert "FuzzyRadio" in dj.generate_station_id()


def test_respond_transition_station_id_success_false(dj: AIDJ):
    fail = LLMResponse(
        content="",
        provider="mock",
        model="m",
        cost=0.0,
        latency=0.0,
        success=False,
        error="x",
    )
    dj._test_router.generate.return_value = fail
    assert "Thanks for tuning in" in dj.respond_to_listener("hi")
    assert "And now" in dj.generate_transition({"title": "A"}, {"title": "B"})
    assert dj.generate_station_id() == "You're listening to QFZZ FuzzyRadio!"


def test_filter_banned_phrases_when_memory_raises(dj: AIDJ):
    dj._test_state.get_dj_memory.side_effect = RuntimeError("memory gone")
    filtered = dj._filter_banned_phrases("This is AI generated music")
    assert "AI" not in filtered
    assert "generated" not in filtered


def test_tts_init_unavailable_and_exception(personas_path: str):
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        with patch("qfzz.dj.ai_dj.TTSClient") as tts_cls:
            client = MagicMock()
            client.is_available.return_value = False
            tts_cls.return_value = client
            dj = AIDJ(persona="energetic", enable_tts=True, personas_config_path=personas_path)
            assert dj.tts_client is None

        with patch("qfzz.dj.ai_dj.TTSClient", side_effect=RuntimeError("no sdk")):
            dj2 = AIDJ(persona="energetic", enable_tts=True, personas_config_path=personas_path)
            assert dj2.tts_client is None


def test_synthesize_speech_paths(dj: AIDJ):
    assert dj.synthesize_speech("hello") is None
    tts = MagicMock()
    tts.synthesize.return_value = b"audio"
    dj.tts_client = tts
    assert dj.synthesize_speech("hello") == b"audio"
    tts.synthesize.side_effect = RuntimeError("synth fail")
    assert dj.synthesize_speech("hello") is None


def test_storyteller_prompt_and_persona_helpers(personas_path: str):
    with patch("qfzz.dj.ai_dj.LLMRouter"), patch("qfzz.dj.ai_dj.StateManager"):
        dj = AIDJ(persona="storyteller", personas_config_path=personas_path)
    prompt = dj._build_intro_prompt({"title": "Long Journey", "artist": "X", "genre": "folk"})
    assert "captivating stories" in prompt
    assert "Long Journey" in prompt
    assert dj.get_persona_description() == "Story DJ"
    assert set(dj.get_available_personas()) >= {"energetic", "storyteller"}
