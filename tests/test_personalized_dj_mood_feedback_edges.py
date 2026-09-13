"""Mood preference updates from PersonalizedDJ feedback path."""

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_like_and_skip_update_mood_weights():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj.add_content(
        [
            {
                "track_id": "m1",
                "genre": "ambient",
                "artist": "Soft",
                "mood": "calm",
            }
        ]
    )
    dj.record_feedback("u1", "m1", "like")
    profile = dj.get_profile("u1")
    assert profile is not None
    assert abs(profile.moods["calm"] - 0.6) < 1e-9

    dj.record_feedback("u1", "m1", "skip")
    assert abs(profile.moods["calm"] - 0.55) < 1e-9


def test_favorite_clamps_mood_to_one():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj.add_content(
        [{"track_id": "m2", "genre": "jazz", "artist": "Sax", "mood": "cool"}]
    )
    for _ in range(20):
        dj.record_feedback("u2", "m2", "favorite")
    profile = dj.get_profile("u2")
    assert profile.moods["cool"] == 1.0
