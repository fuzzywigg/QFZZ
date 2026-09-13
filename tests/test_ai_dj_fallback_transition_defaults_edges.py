"""AIDJ fallback transition defaults when next track has no title."""

from qfzz.dj.ai_dj import AIDJ


def test_fallback_transition_missing_next_title():
    dj = AIDJ.__new__(AIDJ)
    text = AIDJ._get_fallback_transition(
        dj,
        {"title": "Now"},
        {},
    )
    assert "the next track" in text
    assert text.startswith("And now,")
