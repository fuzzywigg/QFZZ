"""Tests for PersonalizedDJ recommendation and feedback."""

from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.profiles import UserProfile


class TestPersonalizedDJ:
    def test_get_or_create_profile_with_preferences(self):
        dj = PersonalizedDJ()
        profile = dj.get_or_create_profile(
            "user-a",
            initial_preferences={
                "genres": {"jazz": 0.9},
                "artists": {"Coltrane": 0.8},
                "energy_level": 0.7,
                "discovery_factor": 0.4,
            },
        )
        assert isinstance(profile, UserProfile)
        assert profile.genres["jazz"] == 0.9
        assert profile.artists["Coltrane"] == 0.8
        again = dj.get_or_create_profile("user-a")
        assert again is profile

    def test_recommend_returns_ranked_tracks(self):
        dj = PersonalizedDJ()
        recs = dj.recommend("user-b", preferences={"genres": {"ambient": 1.0}})
        assert isinstance(recs, list)
        assert len(recs) > 0
        assert "track_id" in recs[0]
        assert "genre" in recs[0] or "title" in recs[0]

    def test_record_feedback_updates_history(self):
        dj = PersonalizedDJ()
        dj.get_or_create_profile("user-c")
        dj.record_feedback("user-c", "track_0001", "like", rating=0.9)
        profile = dj.get_or_create_profile("user-c")
        assert any(i.get("track_id") == "track_0001" for i in profile.interaction_history)

    def test_catalog_override(self):
        dj = PersonalizedDJ()
        catalog = [
            {
                "track_id": "c1",
                "title": "Catalog One",
                "artist": "A",
                "genre": "rock",
                "energy": 0.5,
                "tempo": "medium",
                "content_id": "c1",
                "creator_id": "creator",
            }
        ]
        dj._content_catalog = catalog
        recs = dj.recommend("user-d", preferences={"genres": {"rock": 1.0}})
        assert any(t["track_id"] == "c1" for t in recs)
