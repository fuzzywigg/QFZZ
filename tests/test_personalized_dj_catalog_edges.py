"""Catalog / persona / discovery / feedback edge paths for PersonalizedDJ."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def _dj(**kwargs) -> PersonalizedDJ:
    return PersonalizedDJ(enable_ai_dj=False, **kwargs)


def test_get_profile_missing_returns_none():
    dj = _dj()
    assert dj.get_profile("missing") is None


def test_add_content_empty_and_append():
    dj = _dj()
    before = len(dj._content_catalog)
    dj.add_content([])
    assert len(dj._content_catalog) == before
    dj.add_content(
        [
            {
                "track_id": "x1",
                "title": "X",
                "artist": "A",
                "genre": "ambient",
                "energy": 0.4,
                "tempo": "slow",
            }
        ]
    )
    assert any(t["track_id"] == "x1" for t in dj._content_catalog)


def test_apply_discovery_empty_and_zero_factor():
    dj = _dj()
    assert dj._apply_discovery([], 0.5) == []
    scored = [(1.0, {"track_id": "a"}), (0.5, {"track_id": "b"}), (0.1, {"track_id": "c"})]
    out = dj._apply_discovery(scored, 0.0)
    assert [t["track_id"] for t in out] == ["a", "b", "c"]


def test_feedback_updates_genre_only_when_track_in_catalog():
    dj = _dj()
    dj._content_catalog = [
        {
            "track_id": "t1",
            "genre": "jazz",
            "artist": "Miles",
            "mood": "cool",
            "title": "Blue",
        }
    ]
    dj.get_or_create_profile("u1", initial_preferences={"genres": {"jazz": 0.5}})
    dj.record_feedback("u1", "unknown", "like")
    profile = dj.get_profile("u1")
    assert profile.genres.get("jazz") == 0.5

    dj.record_feedback("u1", "t1", "like")
    assert profile.genres["jazz"] > 0.5
    dj.record_feedback("u1", "t1", "dislike")
    assert profile.genres["jazz"] < 0.7
    dj.record_feedback("u1", "t1", "skip")
    dj.record_feedback("u1", "t1", "favorite")
    assert profile.artists.get("Miles", 0) > 0.4


def test_generate_station_id_fallback_without_ai_dj():
    dj = _dj()
    assert dj.ai_dj is None
    assert "FuzzyRadio" in dj.generate_station_id()
    assert dj.get_ai_dj_persona() is None


def test_set_ai_dj_persona_success_and_failure():
    dj = _dj()
    with patch("qfzz.dj.personalized_dj.AIDJ") as aidj_cls:
        instance = MagicMock()
        instance.get_persona_name.return_value = "Chill Wave"
        aidj_cls.return_value = instance
        assert dj.set_ai_dj_persona("chill") is True
        assert dj.get_ai_dj_persona() == "Chill Wave"

    with patch("qfzz.dj.personalized_dj.AIDJ", side_effect=RuntimeError("boom")):
        assert dj.set_ai_dj_persona("bad") is False


def test_max_tracks_clamp_and_empty_fallback_text():
    dj = _dj()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {
        "success": False,
        "text": "",
        "provider": "None",
    }
    with patch.object(dj, "recommend", return_value=[]):
        payload = dj.generate_llm_recommendation_response("u1", max_tracks=0)
    assert payload["recommendations"] == []
    assert "couldn't fetch" in payload["response"]

    dj._content_catalog = [
        {
            "track_id": f"t{i}",
            "title": f"T{i}",
            "artist": "A",
            "genre": "ambient",
            "energy": 0.3,
            "tempo": "slow",
            "content_id": f"c{i}",
            "creator_id": "cr",
        }
        for i in range(25)
    ]
    payload = dj.generate_llm_recommendation_response("u1", max_tracks=99)
    assert len(payload["recommendations"]) <= 20
    assert payload["used_fallback"] is True
