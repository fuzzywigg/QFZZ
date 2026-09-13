"""Tests for qfzz.dj.profiles.UserProfile."""

from datetime import datetime

import pytest

from qfzz.dj.profiles import UserProfile


class TestUserProfileValidation:
    def test_defaults(self):
        profile = UserProfile(user_id="u1")
        assert profile.energy_level == 0.5
        assert profile.tempo_preference == "medium"
        assert profile.discovery_factor == 0.3
        assert profile.genres == {}
        assert profile.interaction_history == []

    def test_empty_user_id_raises(self):
        with pytest.raises(ValueError, match="user_id"):
            UserProfile(user_id="")

    def test_invalid_energy_level_raises(self):
        with pytest.raises(ValueError, match="energy_level"):
            UserProfile(user_id="u1", energy_level=1.5)

    def test_invalid_tempo_raises(self):
        with pytest.raises(ValueError, match="tempo_preference"):
            UserProfile(user_id="u1", tempo_preference="blazing")

    def test_invalid_discovery_factor_raises(self):
        with pytest.raises(ValueError, match="discovery_factor"):
            UserProfile(user_id="u1", discovery_factor=-0.1)

    def test_varied_tempo_allowed(self):
        profile = UserProfile(user_id="u1", tempo_preference="varied")
        assert profile.tempo_preference == "varied"


class TestUserProfilePreferences:
    def test_update_genre_preference(self):
        profile = UserProfile(user_id="u1")
        before = profile.updated_at
        profile.update_genre_preference("jazz", 0.9)
        assert profile.genres["jazz"] == 0.9
        assert profile.updated_at >= before

    def test_update_genre_invalid_weight(self):
        profile = UserProfile(user_id="u1")
        with pytest.raises(ValueError, match="Weight"):
            profile.update_genre_preference("jazz", 2.0)

    def test_update_artist_and_mood(self):
        profile = UserProfile(user_id="u1")
        profile.update_artist_preference("Miles Davis", 0.8)
        profile.update_mood_preference("chill", 0.7)
        assert profile.artists["Miles Davis"] == 0.8
        assert profile.moods["chill"] == 0.7

    def test_update_artist_invalid_weight(self):
        profile = UserProfile(user_id="u1")
        with pytest.raises(ValueError, match="Weight"):
            profile.update_artist_preference("x", -0.1)

    def test_update_mood_invalid_weight(self):
        profile = UserProfile(user_id="u1")
        with pytest.raises(ValueError, match="Weight"):
            profile.update_mood_preference("x", 1.1)

    def test_add_interaction_adds_timestamp(self):
        profile = UserProfile(user_id="u1")
        profile.add_interaction({"action": "skip", "track_id": "t1"})
        assert len(profile.interaction_history) == 1
        assert "timestamp" in profile.interaction_history[0]
        datetime.fromisoformat(profile.interaction_history[0]["timestamp"])

    def test_interaction_history_capped_at_1000(self):
        profile = UserProfile(user_id="u1")
        for i in range(1005):
            profile.add_interaction({"n": i})
        assert len(profile.interaction_history) == 1000
        assert profile.interaction_history[0]["n"] == 5
        assert profile.interaction_history[-1]["n"] == 1004

    def test_get_top_genres_and_artists(self):
        profile = UserProfile(user_id="u1")
        profile.genres = {"a": 0.1, "b": 0.9, "c": 0.5}
        profile.artists = {"x": 0.2, "y": 0.8}
        assert profile.get_top_genres(2) == ["b", "c"]
        assert profile.get_top_artists(1) == ["y"]

    def test_to_dict_roundtrip_fields(self):
        profile = UserProfile(user_id="u1", energy_level=0.7)
        profile.update_genre_preference("rock", 0.6)
        data = profile.to_dict()
        assert data["user_id"] == "u1"
        assert data["energy_level"] == 0.7
        assert data["genres"]["rock"] == 0.6
        assert "created_at" in data and "updated_at" in data
