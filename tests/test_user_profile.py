"""Tests for UserProfile dataclass defaults."""

from datetime import datetime

from qfzz.dj.user_profile import UserProfile


def test_user_profile_defaults():
    profile = UserProfile(user_id="u1", name="Ada")
    assert profile.user_id == "u1"
    assert profile.name == "Ada"
    assert profile.music_preferences == []
    assert profile.interaction_history == []
    assert profile.trust_score == 0.5
    assert profile.community_connections == []
    assert isinstance(profile.created_at, datetime)


def test_user_profile_custom_fields():
    profile = UserProfile(
        user_id="u2",
        name="Grace",
        music_preferences=["jazz", "ambient"],
        trust_score=0.9,
        community_connections=["u1"],
    )
    assert profile.music_preferences == ["jazz", "ambient"]
    assert profile.trust_score == 0.9
    assert profile.community_connections == ["u1"]
