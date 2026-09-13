"""UserProfile inclusive preference boundaries and empty top-N edges."""

from qfzz.dj.profiles import UserProfile


def test_energy_and_discovery_inclusive_bounds():
    low = UserProfile(user_id="u1", energy_level=0.0, discovery_factor=0.0)
    high = UserProfile(user_id="u2", energy_level=1.0, discovery_factor=1.0)
    assert low.energy_level == 0.0
    assert high.discovery_factor == 1.0


def test_preference_weight_zero_and_top_n_empty():
    profile = UserProfile(user_id="u3")
    profile.update_genre_preference("ambient", 0.0)
    profile.update_artist_preference("none", 0.0)
    profile.update_mood_preference("calm", 0.0)
    assert profile.genres["ambient"] == 0.0
    assert profile.get_top_genres(0) == []
    assert profile.get_top_artists(0) == []
    assert profile.get_top_genres() == ["ambient"]


def test_add_interaction_mutates_caller_dict_with_timestamp():
    profile = UserProfile(user_id="u4")
    payload = {"action": "skip"}
    profile.add_interaction(payload)
    assert "timestamp" in payload
    assert profile.interaction_history[0] is payload
