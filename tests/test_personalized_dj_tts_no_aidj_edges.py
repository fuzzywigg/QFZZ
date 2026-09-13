"""PersonalizedDJ include_tts with ai_dj None stays TTS-off."""

from unittest.mock import MagicMock

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_include_tts_without_ai_dj_sets_tts_included_false():
    dj = PersonalizedDJ(enable_ai_dj=False)
    assert dj.ai_dj is None
    dj._content_catalog = [
        {
            "track_id": "t1",
            "title": "Orbit",
            "artist": "Nova",
            "genre": "electronic",
            "energy": 0.5,
            "tempo": "medium",
            "content_id": "c1",
            "creator_id": "cr",
        }
    ]
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "cloud pick",
        "provider": "Groq",
        "success": True,
    }

    payload = dj.generate_llm_recommendation_response(
        user_id="u1",
        message="go",
        include_tts=True,
        max_tracks=1,
    )

    assert payload["tts_included"] is False
    assert "tts_audio_base64" not in payload
    assert payload["llm_online"] is True
