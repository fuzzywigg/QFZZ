"""Tests for LLM-backed PersonalizedDJ recommendation payloads."""

from unittest.mock import MagicMock

from qfzz.dj.personalized_dj import PersonalizedDJ


def _build_catalog():
    return [
        {"track_id": "t1", "title": "Orbit", "artist": "Nova", "genre": "electronic", "energy": 0.8},
        {"track_id": "t2", "title": "Quiet Tide", "artist": "Delta", "genre": "ambient", "energy": 0.4},
        {"track_id": "t3", "title": "Signal", "artist": "Echo", "genre": "electronic", "energy": 0.7},
    ]


def test_generate_llm_recommendation_response_prefers_local_provider():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _build_catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "Spin Orbit and Signal to keep energy high.",
        "provider": "Ollama",
        "success": True,
    }

    payload = dj.generate_llm_recommendation_response(
        user_id="listener_1",
        message="Give me high-energy picks",
        max_tracks=2,
    )

    assert payload["provider"] == "Ollama"
    assert payload["llm_online"] is True
    assert payload["used_fallback"] is False
    assert payload["execution_mode"] == "edge-local"
    assert len(payload["recommendations"]) == 2


def test_generate_llm_recommendation_response_falls_back_when_llm_offline():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _build_catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "placeholder",
        "provider": "Mock",
        "success": True,
    }

    payload = dj.generate_llm_recommendation_response(
        user_id="listener_2",
        message="Recommend something chill",
        max_tracks=3,
    )

    assert payload["llm_online"] is False
    assert payload["used_fallback"] is True
    assert payload["execution_mode"] == "fallback"
    assert "Try" in payload["response"]
    assert 1 <= len(payload["recommendations"]) <= 3


def test_generate_llm_recommendation_response_can_include_tts():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _build_catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "Queue Orbit followed by Signal.",
        "provider": "Groq",
        "success": True,
    }
    dj.ai_dj = MagicMock()
    dj.ai_dj.synthesize_speech.return_value = b"audio-bytes"

    payload = dj.generate_llm_recommendation_response(
        user_id="listener_3",
        message="Something electronic",
        include_tts=True,
    )

    assert payload["tts_included"] is True
    assert payload["tts_audio_base64"] == "YXVkaW8tYnl0ZXM="
    assert payload["tts_format"] == "mp3"
