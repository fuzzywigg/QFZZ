"""AIDJ banned-phrase filter can empty the announcement text."""

from unittest.mock import MagicMock

from qfzz.dj.ai_dj import AIDJ


def test_banned_filter_empties_entirely_banned_text():
    dj = AIDJ.__new__(AIDJ)
    dj.persona_config = {"banned_phrases": ["AI", "language model"]}
    dj.state = MagicMock()
    dj.state.get_dj_memory.return_value = {"banned_phrases": [], "conversation_history": []}
    assert dj._filter_banned_phrases("AI language model") == ""
    assert dj._filter_banned_phrases("AI") == ""
    assert dj._filter_banned_phrases("language model") == ""


def test_banned_filter_case_insensitive_partial_strip():
    dj = AIDJ.__new__(AIDJ)
    dj.persona_config = {"banned_phrases": ["as an artificial intelligence"]}
    dj.state = MagicMock()
    dj.state.get_dj_memory.return_value = {"banned_phrases": [], "conversation_history": []}
    out = dj._filter_banned_phrases("Hello As An Artificial Intelligence friend")
    assert "artificial intelligence" not in out.lower()
    assert "Hello" in out
    assert "friend" in out
