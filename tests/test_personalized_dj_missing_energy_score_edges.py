"""PersonalizedDJ scoring when track omits energy key."""

from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.profiles import UserProfile


def test_missing_energy_scores_below_matching_energy():
    dj = PersonalizedDJ(enable_ai_dj=False)
    profile = UserProfile(user_id="u")
    profile.energy_level = 0.7

    with_energy = {"genre": "ambient", "artist": "A", "energy": 0.7}
    missing_energy = {"genre": "ambient", "artist": "A"}

    s_with = dj._calculate_track_score(with_energy, profile)
    s_missing = dj._calculate_track_score(missing_energy, profile)
    assert 0.0 <= s_missing <= 1.0
    assert 0.0 <= s_with <= 1.0
    assert s_missing < s_with
