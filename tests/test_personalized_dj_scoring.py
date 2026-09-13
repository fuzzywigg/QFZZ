"""Deepen PersonalizedDJ scoring, feedback, catalog, and persona APIs."""

from unittest.mock import MagicMock, patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def _catalog_track(**overrides):
    base = {
        "track_id": "t1",
        "title": "Track One",
        "artist": "Known Artist",
        "genre": "jazz",
        "mood": "mellow",
        "energy": 0.5,
        "tempo": "medium",
        "duration": 200,
        "content_id": "c1",
        "creator_id": "creator-1",
    }
    base.update(overrides)
    return base


def _make_dj(enable_ai_dj=True):
    with (
        patch("qfzz.dj.personalized_dj.QFZZKnowledgeGraph"),
        patch("qfzz.dj.personalized_dj.ContentScanner"),
        patch("qfzz.dj.personalized_dj.SovereignLedger"),
        patch("qfzz.dj.personalized_dj.ContentFetcher"),
        patch("qfzz.dj.personalized_dj.LLMRouter"),
        patch("qfzz.dj.personalized_dj.AIDJ") as ai_cls,
    ):
        ai = MagicMock()
        ai.get_persona_name.return_value = "Energetic"
        ai.generate_station_id.return_value = "Station ID from AI DJ"
        ai_cls.return_value = ai
        dj = PersonalizedDJ(enable_ai_dj=enable_ai_dj)
        dj._test_ai_cls = ai_cls
        dj._test_ai = ai
        return dj


class TestPersonalizedDJScoring:
    def test_exact_genre_artist_tempo_mood_outranks_mismatch(self):
        dj = _make_dj()
        match = _catalog_track(track_id="match", energy=0.7)
        mismatch = _catalog_track(
            track_id="mismatch",
            genre="metal",
            artist="Other",
            mood="energetic",
            energy=0.1,
            tempo="fast",
        )
        dj.add_content([match, mismatch])
        profile = dj.get_or_create_profile(
            "u-score",
            initial_preferences={
                "genres": {"jazz": 1.0},
                "artists": {"Known Artist": 1.0},
                "energy_level": 0.7,
                "discovery_factor": 0.0,
            },
        )
        # get_or_create_profile only wires genres/artists/energy/discovery
        profile.tempo_preference = "medium"
        profile.update_mood_preference("mellow", 1.0)
        recs = dj.recommend("u-score")
        assert recs[0]["track_id"] == "match"

    def test_similar_genre_scores_above_unrelated(self):
        dj = _make_dj()
        similar = _catalog_track(track_id="sim", genre="blues", artist="X", mood="calm")
        unrelated = _catalog_track(track_id="unrel", genre="trap", artist="Y", mood="calm")
        dj.add_content([similar, unrelated])
        profile = dj.get_or_create_profile(
            "u-sim",
            initial_preferences={
                "genres": {"jazz": 1.0},
                "discovery_factor": 0.0,
                "energy_level": 0.5,
            },
        )
        profile.tempo_preference = "varied"
        score_sim = dj._calculate_track_score(similar, profile)
        score_unrel = dj._calculate_track_score(unrelated, profile)
        assert score_sim > score_unrel

    def test_discovery_factor_zero_keeps_full_ranked_list(self):
        dj = _make_dj()
        tracks = [_catalog_track(track_id=f"t{i}", energy=i / 10) for i in range(5)]
        dj.add_content(tracks)
        dj.get_or_create_profile(
            "u-disc",
            initial_preferences={"genres": {"jazz": 1.0}, "discovery_factor": 0.0},
        )
        recs = dj.recommend("u-disc")
        assert len(recs) == 5

    def test_empty_scored_tracks_returns_empty_discovery(self):
        dj = _make_dj()
        assert dj._apply_discovery([], 0.5) == []


class TestPersonalizedDJFeedback:
    def test_like_raises_genre_artist_mood_weights(self):
        dj = _make_dj()
        track = _catalog_track(genre="ambient", artist="Nova", mood="calm")
        dj.add_content([track])
        profile = dj.get_or_create_profile("u-like")
        before_genre = profile.genres.get("ambient", 0.5)
        before_artist = profile.artists.get("Nova", 0.5)
        before_mood = profile.moods.get("calm", 0.5)
        dj.record_feedback("u-like", "t1", "like")
        assert profile.genres["ambient"] == before_genre + 0.1
        assert profile.artists["Nova"] == before_artist + 0.1
        assert profile.moods["calm"] == before_mood + 0.1

    def test_dislike_and_skip_lower_weights(self):
        dj = _make_dj()
        track = _catalog_track(genre="pop", artist="Popstar", mood="upbeat")
        dj.add_content([track])
        profile = dj.get_or_create_profile(
            "u-neg",
            initial_preferences={
                "genres": {"pop": 0.6},
                "artists": {"Popstar": 0.6},
            },
        )
        profile.update_mood_preference("upbeat", 0.6)
        dj.record_feedback("u-neg", "t1", "dislike")
        assert profile.genres["pop"] == 0.5
        dj.record_feedback("u-neg", "t1", "skip")
        assert abs(profile.genres["pop"] - 0.45) < 1e-9

    def test_favorite_and_explicit_rating_override_strength(self):
        dj = _make_dj()
        track = _catalog_track(genre="folk", artist="Folkie", mood="calm")
        dj.add_content([track])
        profile = dj.get_or_create_profile("u-fav")
        dj.record_feedback("u-fav", "t1", "favorite")
        assert profile.genres["folk"] == 0.7  # 0.5 + 0.2
        dj.record_feedback("u-fav", "t1", "play", rating=1.0)
        # rating strength = (1.0 - 0.5) * 0.2 = 0.1
        assert abs(profile.genres["folk"] - 0.8) < 1e-9

    def test_feedback_unknown_track_is_noop_on_preferences(self):
        dj = _make_dj()
        profile = dj.get_or_create_profile("u-miss")
        dj.record_feedback("u-miss", "missing-track", "like")
        assert profile.genres == {}
        assert any(i["track_id"] == "missing-track" for i in profile.interaction_history)


class TestPersonalizedDJCatalogAndPersona:
    def test_add_content_and_get_profile(self):
        dj = _make_dj()
        assert dj.get_profile("nobody") is None
        dj.add_content([_catalog_track()])
        assert len(dj._content_catalog) == 1
        dj.get_or_create_profile("u1")
        assert dj.get_profile("u1") is not None

    def test_persona_and_station_id_with_ai(self):
        dj = _make_dj(enable_ai_dj=True)
        assert dj.get_ai_dj_persona() == "Energetic"
        assert dj.generate_station_id() == "Station ID from AI DJ"
        with patch("qfzz.dj.personalized_dj.AIDJ") as ai_cls:
            ai = MagicMock()
            ai.get_persona_name.return_value = "Chill"
            ai_cls.return_value = ai
            assert dj.set_ai_dj_persona("chill") is True
            assert dj.get_ai_dj_persona() == "Chill"

    def test_persona_and_station_id_without_ai(self):
        dj = _make_dj(enable_ai_dj=False)
        dj.ai_dj = None
        assert dj.get_ai_dj_persona() is None
        assert dj.generate_station_id() == "You're listening to QFZZ FuzzyRadio!"

    def test_set_ai_dj_persona_failure_returns_false(self):
        dj = _make_dj(enable_ai_dj=True)
        with patch("qfzz.dj.personalized_dj.AIDJ", side_effect=RuntimeError("boom")):
            assert dj.set_ai_dj_persona("chill") is False
