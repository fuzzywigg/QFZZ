"""PersonalizedDJ fallback recommendation copy with/without favorite genre."""

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
            "tempo": "fast",
            "content_id": "c1",
            "creator_id": "cr",
        },
        {
            "track_id": "t2",
            "title": "Quiet Tide",
            "artist": "Delta",
            "genre": "ambient",
            "energy": 0.3,
            "tempo": "slow",
            "content_id": "c2",
            "creator_id": "cr",
        },
    ]


def test_fallback_text_includes_leaned_into_favorite_genre():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "placeholder",
        "provider": "Mock",
        "success": True,
    }
    dj.get_or_create_profile(
        "fan",
        initial_preferences={"genres": {"electronic": 0.9, "ambient": 0.2}},
    )

    payload = dj.generate_llm_recommendation_response(
        user_id="fan",
        message="keep it electronic",
        max_tracks=2,
    )

    assert payload["used_fallback"] is True
    assert "leaned into your electronic preference" in payload["response"]
    assert "Try" in payload["response"]


def test_fallback_text_without_genres_uses_refine_copy():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = _catalog()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "text": "",
        "provider": "None",
        "success": False,
    }
    # profile with empty genres
    dj.get_or_create_profile("newcomer")

    payload = dj.generate_llm_recommendation_response(
        user_id="newcomer",
        message="surprise me",
        max_tracks=2,
    )

    assert payload["used_fallback"] is True
    assert "I'll refine this list as you share more feedback" in payload["response"]
    assert "leaned into" not in payload["response"]
