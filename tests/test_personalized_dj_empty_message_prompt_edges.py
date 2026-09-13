"""PersonalizedDJ empty/whitespace message uses default vibe prompt."""

from unittest.mock import MagicMock

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_empty_and_whitespace_message_default_listener_request():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj._content_catalog = [
        {
            "track_id": "t1",
            "title": "Orbit",
            "artist": "Nova",
            "genre": "electronic",
            "energy": 0.8,
            "tempo": "fast",
            "content_id": "c1",
            "creator_id": "cr",
        }
    ]
    captured = []

    def capture_generate(prompt, **kwargs):
        captured.append(prompt)
        return {"text": "ok", "provider": "Mock", "success": True}

    dj.llm_router = MagicMock()
    dj.llm_router.generate.side_effect = capture_generate

    dj.generate_llm_recommendation_response(user_id="u1", message="")
    dj.generate_llm_recommendation_response(user_id="u1", message="   \n\t  ")

    assert len(captured) == 2
    for prompt in captured:
        assert "Listener request: Recommend tracks for my current vibe." in prompt
