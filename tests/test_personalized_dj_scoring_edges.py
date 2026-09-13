"""Scoring / discovery / segue / profile edge paths for PersonalizedDJ."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.profiles import UserProfile


def _dj(**kwargs) -> PersonalizedDJ:
    return PersonalizedDJ(enable_ai_dj=False, **kwargs)


def test_calculate_track_score_genre_artist_energy_tempo_mood():
    dj = _dj()
    profile = UserProfile(user_id="u")
    profile.update_genre_preference("rock", 1.0)
    profile.update_artist_preference("Known", 0.8)
    profile.energy_level = 0.5
    profile.tempo_preference = "medium"
    profile.update_mood_preference("calm", 1.0)

    exact = {
        "genre": "rock",
        "artist": "Known",
        "energy": 0.5,
        "tempo": "medium",
        "mood": "calm",
    }
    similar = {
        "genre": "indie",  # similar to rock
        "artist": "Other",
        "energy": 0.5,
        "tempo": "medium",
        "mood": "calm",
    }
    distant = {
        "genre": "classical",
        "artist": "Other",
        "energy": 0.0,
        "tempo": "fast",
        "mood": "upbeat",
    }

    s_exact = dj._calculate_track_score(exact, profile)
    s_similar = dj._calculate_track_score(similar, profile)
    s_distant = dj._calculate_track_score(distant, profile)
    assert 0.0 <= s_exact <= 1.0
    assert s_exact > s_similar > s_distant

    profile.tempo_preference = "varied"
    s_varied = dj._calculate_track_score(distant, profile)
    assert s_varied >= s_distant


def test_apply_discovery_mid_factor_injects_from_pool():
    dj = _dj()
    scored = [(1.0 - i * 0.05, {"track_id": f"t{i}"}) for i in range(20)]
    with patch("qfzz.dj.personalized_dj.random.sample", side_effect=lambda pool, n: pool[:n]):
        out = dj._apply_discovery(scored, 0.4)
    ids = [t["track_id"] for t in out]
    assert "t0" in ids
    assert len(out) > int(len(scored) * 0.6)  # includes discovery extras


def test_generate_segue_fingerprint_and_no_rels():
    dj = _dj()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {"text": "segue text"}
    dj.ledger = MagicMock()

    prev = {
        "title": "A",
        "artist": "Same",
        "genre": "ambient",
        "fingerprint": {"key": "C", "bpm": 90},
    }
    nxt = {
        "title": "B",
        "artist": "Same",
        "genre": "ambient",
        "fingerprint": {"key": "C", "bpm": 120},
    }
    text = dj.generate_segue(prev, nxt)
    assert text == "segue text"
    prompt = dj.llm_router.generate.call_args[0][0]
    assert "same artist" in prompt
    assert "same vibe" in prompt
    assert "staying in the key of C" in prompt
    assert "bumping up the energy" in prompt
    dj.ledger.record_event.assert_called()

    slow = {
        "title": "C",
        "artist": "X",
        "genre": "jazz",
        "fingerprint": {"key": "D", "bpm": 70},
    }
    dj.generate_segue(
        {"title": "P", "artist": "Y", "genre": "rock", "fingerprint": {"key": "E", "bpm": 100}},
        slow,
    )
    prompt2 = dj.llm_router.generate.call_args[0][0]
    assert "slowing things down" in prompt2 or "switching gears" in prompt2

    dj.generate_segue(
        {"title": "P", "artist": "Y", "genre": "rock"},
        {"title": "N", "artist": "Z", "genre": "pop"},
    )
    prompt3 = dj.llm_router.generate.call_args[0][0]
    assert "switching gears" in prompt3


def test_generate_segue_first_track_without_ai():
    dj = _dj()
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {"text": "intro"}
    dj.ledger = MagicMock()
    out = dj.generate_segue(None, {"title": "First", "artist": "Solo"})
    assert out == "intro"
    prompt = dj.llm_router.generate.call_args[0][0]
    assert "Introduce the first track" in prompt
    assert "First" in prompt


def test_record_feedback_play_with_rating_and_partial_track():
    dj = _dj()
    dj._content_catalog = [
        {"track_id": "t1", "genre": "ambient", "title": "NoArtist"},
        {"track_id": "t2", "artist": "OnlyArtist", "title": "NoGenre"},
    ]
    dj.get_or_create_profile("u1")
    dj.record_feedback("u1", "t1", "play")
    profile = dj.get_profile("u1")
    assert profile.genres.get("ambient", 0) > 0.5

    before = profile.artists.copy()
    dj.record_feedback("u1", "t2", "play", rating=1.0)
    assert profile.artists.get("OnlyArtist", 0) >= before.get("OnlyArtist", 0.5)


def test_get_candidate_tracks_sample_with_and_without_genres():
    dj = _dj()
    dj._content_catalog = []
    empty_profile = UserProfile(user_id="e")
    samples = dj._get_candidate_tracks(empty_profile)
    assert len(samples) == 50
    assert samples[0]["track_id"].startswith("track_")

    filled = UserProfile(user_id="f")
    filled.update_genre_preference("jazz", 0.9)
    with patch("qfzz.dj.personalized_dj.random.choice", return_value="jazz"):
        samples2 = dj._generate_sample_tracks(filled)
    assert all(t["genre"] == "jazz" for t in samples2)


def test_get_or_create_profile_partial_prefs():
    dj = _dj()
    p1 = dj.get_or_create_profile("a", initial_preferences={"genres": {"rock": 0.7}})
    assert p1.genres["rock"] == 0.7
    p2 = dj.get_or_create_profile("b", initial_preferences={"energy_level": 0.2})
    assert p2.energy_level == 0.2
    p3 = dj.get_or_create_profile(
        "c",
        initial_preferences={"artists": {"Zed": 0.6}, "discovery_factor": 0.3},
    )
    assert p3.artists["Zed"] == 0.6
    assert p3.discovery_factor == 0.3
    # second call returns same instance
    assert dj.get_or_create_profile("a") is p1
