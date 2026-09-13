"""PersonalizedDJ feedback clamp / rating override / similar-genres edges."""

from qfzz.dj.personalized_dj import PersonalizedDJ


def _dj() -> PersonalizedDJ:
    return PersonalizedDJ(enable_ai_dj=False)


def test_repeated_dislike_clamps_genre_to_zero():
    dj = _dj()
    dj.add_content(
        [{"track_id": "t1", "genre": "rock", "artist": "Band", "mood": "calm"}]
    )
    for _ in range(20):
        dj.record_feedback("u1", "t1", "dislike")
    profile = dj.get_profile("u1")
    assert profile is not None
    assert profile.genres["rock"] == 0.0
    assert profile.artists["Band"] == 0.0


def test_repeated_favorite_clamps_to_one():
    dj = _dj()
    dj.add_content(
        [{"track_id": "t2", "genre": "jazz", "artist": "Sax", "mood": "cool"}]
    )
    for _ in range(20):
        dj.record_feedback("u2", "t2", "favorite")
    profile = dj.get_profile("u2")
    assert profile.genres["jazz"] == 1.0
    assert profile.artists["Sax"] == 1.0


def test_explicit_rating_overrides_interaction_strength():
    dj = _dj()
    dj.add_content([{"track_id": "t3", "genre": "pop", "artist": "PopStar"}])
    dj.record_feedback("u3", "t3", "like", rating=0.0)
    low = dj.get_profile("u3").genres["pop"]
    dj2 = _dj()
    dj2.add_content([{"track_id": "t3", "genre": "pop", "artist": "PopStar"}])
    dj2.record_feedback("u3", "t3", "dislike", rating=1.0)
    high = dj2.get_profile("u3").genres["pop"]
    # rating 0 → strength -0.1; rating 1 → strength +0.1 from 0.5 default
    assert abs(low - 0.4) < 1e-9
    assert abs(high - 0.6) < 1e-9


def test_get_similar_genres_known_and_unknown():
    dj = _dj()
    similar = dj._get_similar_genres(["rock", "xyz"])
    assert "indie" in similar
    assert "alternative" in similar
    assert dj._get_similar_genres(["xyz"]) == []
