"""PersonalizedDJ sparse scoring and BPM boundary segue edges."""

from unittest.mock import MagicMock

from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.profiles import UserProfile


def test_sparse_track_score_stays_in_unit_interval_and_below_full_match():
    dj = PersonalizedDJ(enable_ai_dj=False)
    profile = UserProfile(user_id="u1")
    profile.update_genre_preference("electronic", 0.9)
    profile.update_artist_preference("Nova", 0.8)
    profile.update_mood_preference("chill", 0.7)
    profile.energy_level = 0.5
    profile.tempo_preference = "medium"
    full = {
        "title": "Full",
        "artist": "Nova",
        "genre": "electronic",
        "energy": 0.5,
        "tempo": "medium",
        "mood": "chill",
    }
    sparse = {"title": "Sparse", "artist": "Other", "genre": "folk"}

    full_score = dj._calculate_track_score(full, profile)
    sparse_score = dj._calculate_track_score(sparse, profile)

    assert 0.0 <= sparse_score <= 1.0
    assert 0.0 <= full_score <= 1.0
    assert sparse_score < full_score


def test_segue_bpm_delta_exactly_ten_does_not_bump_or_slow():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {"text": "segue", "provider": "Mock", "success": True}

    prev = {
        "title": "A",
        "artist": "X",
        "genre": "rock",
        "fingerprint": {"key": "C", "bpm": 120},
    }
    nxt = {
        "title": "B",
        "artist": "Y",
        "genre": "jazz",
        "fingerprint": {"key": "D", "bpm": 130},
    }
    text = dj.generate_segue(prev, nxt)
    assert text == "segue"
    prompt = dj.llm_router.generate.call_args.args[0]
    assert "switching gears" in prompt
    assert "bumping up the energy" not in prompt
    assert "slowing things down" not in prompt
