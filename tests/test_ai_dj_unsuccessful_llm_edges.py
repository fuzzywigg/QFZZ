"""AIDJ respond/transition/station-id when LLM returns success=False or raises."""

from unittest.mock import MagicMock, patch

from qfzz.core.llm_router import LLMResponse
from qfzz.dj.ai_dj import AIDJ


def _fail_response() -> LLMResponse:
    return LLMResponse(
        content="",
        provider="mock",
        model="m",
        cost=0.0,
        latency=0.0,
        success=False,
        error="provider down",
    )


def test_respond_and_transition_use_fallback_when_llm_unsuccessful():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.return_value = _fail_response()
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")

        reply = dj.respond_to_listener("play jazz")
        transition = dj.generate_transition(
            {"title": "Old Tune", "artist": "A"},
            {"title": "New Tune", "artist": "B"},
        )

    assert "Thanks for tuning in" in reply
    assert "And now" in transition
    assert "New Tune" in transition


def test_station_id_exception_uses_static_fallback():
    with (
        patch("qfzz.dj.ai_dj.LLMRouter") as mock_router,
        patch("qfzz.dj.ai_dj.StateManager"),
    ):
        inst = MagicMock()
        inst.generate.side_effect = RuntimeError("router crash")
        mock_router.return_value = inst
        dj = AIDJ(personas_config_path="config/dj-personas.json")
        assert dj.generate_station_id() == "You're listening to QFZZ FuzzyRadio!"
