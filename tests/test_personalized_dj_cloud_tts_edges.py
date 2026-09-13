"""Cloud execution_mode + TTS-null soft-fail on LLM recommendations."""

from unittest.mock import MagicMock

from qfzz.dj.personalized_dj import PersonalizedDJ


def _catalog():
    return [
        {
            "track_id": "t1",
            "title": "Orbit",
            "artist": "Nova",
            "genre": "electronic",
            "energy": 0.8,
        },
    ]


def test_cloud_execution_mode_for_non_ollama_provider():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "Queue Orbit next.",
        "provider": "Groq",
        "success": True,
    }

    payload = dj.generate_llm_recommendation_response(
        user_id="u-cloud",
        message="electronic",
        max_tracks=1,
    )
    assert payload["llm_online"] is True
    assert payload["execution_mode"] == "cloud"
    assert payload["provider"] == "Groq"
    assert payload["used_fallback"] is False


def test_include_tts_null_audio_sets_tts_included_false():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "Spin Orbit.",
        "provider": "Groq",
        "success": True,
    }
    dj.ai_dj = MagicMock()
    dj.ai_dj.synthesize_speech.return_value = None

    payload = dj.generate_llm_recommendation_response(
        user_id="u-tts",
        message="go",
        include_tts=True,
    )
    assert payload["execution_mode"] == "cloud"
    assert payload["tts_included"] is False
    assert "tts_audio_base64" not in payload
