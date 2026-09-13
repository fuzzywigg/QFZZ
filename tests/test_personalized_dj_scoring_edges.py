"""Edge coverage for PersonalizedDJ scoring, similar genres, segue fingerprints, feedback."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.profiles import UserProfile


def _make_dj(**kwargs):
    with patch("qfzz.dj.personalized_dj.QFZZKnowledgeGraph"):
        with patch("qfzz.dj.personalized_dj.ContentScanner"):
            with patch("qfzz.dj.personalized_dj.SovereignLedger") as ledger_cls:
                with patch("qfzz.dj.personalized_dj.ContentFetcher"):
                    with patch("qfzz.dj.personalized_dj.LLMRouter") as router_cls:
                        with patch("qfzz.dj.personalized_dj.AIDJ") as ai_cls:
                            ledger = MagicMock()
                            ledger_cls.return_value = ledger
                            router = MagicMock()
                            router.get_available_providers.return_value = ["Mock"]
                            router.generate.return_value = {"text": "cool segue"}
                            router_cls.return_value = router
                            ai = MagicMock()
                            ai_cls.return_value = ai
                            enable = kwargs.pop("enable_ai_dj", False)
                            dj = PersonalizedDJ(enable_ai_dj=enable, **kwargs)
                            if not enable:
                                dj.ai_dj = None
                            dj._test_ledger = ledger
                            dj._test_router = router
                            return dj


def test_similar_genre_and_exact_genre_scoring():
    dj = _make_dj()
    profile = UserProfile(
        user_id="u1",
        genres={"rock": 1.0},
        artists={"Known": 0.9},
        moods={"upbeat": 0.8},
        energy_level=0.5,
        tempo_preference="varied",
    )
    exact = dj._calculate_track_score(
        {
            "genre": "rock",
            "artist": "Known",
            "energy": 0.5,
            "tempo": "fast",
            "mood": "upbeat",
        },
        profile,
    )
    similar = dj._calculate_track_score(
        {
            "genre": "indie",
            "artist": "Other",
            "energy": 0.5,
            "tempo": "slow",
            "mood": "calm",
        },
        profile,
    )
    assert 0.0 <= exact <= 1.0
    assert 0.0 <= similar <= 1.0
    assert exact > similar


def test_energy_distance_and_clamp():
    dj = _make_dj()
    profile = UserProfile(user_id="u2", energy_level=0.0, tempo_preference="medium")
    far = dj._calculate_track_score({"genre": "x", "energy": 1.0, "tempo": "slow"}, profile)
    near = dj._calculate_track_score({"genre": "x", "energy": 0.0, "tempo": "medium"}, profile)
    assert near >= far
    assert 0.0 <= far <= 1.0


def test_get_similar_genres_unknown_and_known():
    dj = _make_dj()
    assert dj._get_similar_genres(["unknown-genre"]) == []
    similar = dj._get_similar_genres(["rock", "jazz"])
    assert "indie" in similar
    assert "blues" in similar


def test_generate_segue_fingerprint_edges_without_ai():
    dj = _make_dj(enable_ai_dj=False)
    next_track = {"title": "Next", "artist": "A", "genre": "rock"}
    text = dj.generate_segue(None, next_track)
    assert text == "cool segue"
    dj._test_ledger.record_event.assert_called()

    prev = {
        "title": "Prev",
        "artist": "A",
        "genre": "rock",
        "fingerprint": {"key": "Am", "bpm": 100},
    }
    nxt = {
        "title": "Next",
        "artist": "A",
        "genre": "rock",
        "fingerprint": {"key": "Am", "bpm": 120},
    }
    dj.generate_segue(prev, nxt)
    call_kwargs = dj._test_router.generate.call_args
    prompt = call_kwargs[0][0]
    assert "same artist" in prompt
    assert "same vibe" in prompt
    assert "staying in the key of Am" in prompt
    assert "bumping up the energy" in prompt

    slow = {
        "title": "Slow",
        "artist": "B",
        "genre": "pop",
        "fingerprint": {"key": "C", "bpm": 80},
    }
    fast_prev = {
        "title": "Fast",
        "artist": "C",
        "genre": "edm",
        "fingerprint": {"key": "D", "bpm": 130},
    }
    dj.generate_segue(fast_prev, slow)
    prompt2 = dj._test_router.generate.call_args[0][0]
    assert "slowing things down" in prompt2

    unrelated = {"title": "X", "artist": "Y", "genre": "folk"}
    dj.generate_segue({"title": "P", "artist": "Q", "genre": "metal"}, unrelated)
    prompt3 = dj._test_router.generate.call_args[0][0]
    assert "switching gears" in prompt3


def test_record_feedback_play_and_rating():
    dj = _make_dj()
    dj._content_catalog = [
        {
            "track_id": "t1",
            "genre": "rock",
            "artist": "Band",
            "mood": "upbeat",
            "energy": 0.7,
        }
    ]
    dj.record_feedback("user-a", "t1", "play")
    dj.record_feedback("user-a", "t1", "like", rating=0.9)
    profile = dj.get_or_create_profile("user-a")
    assert any(i["type"] == "play" for i in profile.interaction_history)
    assert any(i.get("rating") == 0.9 for i in profile.interaction_history)


def test_generate_sample_tracks_when_catalog_empty_via_recommend():
    dj = _make_dj()
    dj._content_catalog = []
    profile = UserProfile(user_id="u3", genres={"jazz": 0.8})
    samples = dj._generate_sample_tracks(profile)
    assert len(samples) == 50
    assert all(t["genre"] == "jazz" for t in samples)
