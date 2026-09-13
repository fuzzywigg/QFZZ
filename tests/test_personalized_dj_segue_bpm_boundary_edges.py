"""PersonalizedDJ.generate_segue BPM delta exactly ±10 skips energy rel phrases."""

from unittest.mock import MagicMock

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_segue_bpm_delta_exactly_plus_minus_10_skips_energy_phrases():
    dj = PersonalizedDJ(enable_ai_dj=False)
    dj.llm_router = MagicMock()
    dj.llm_router.generate.return_value = {"text": "neutral"}
    dj.ledger = MagicMock()

    prev = {
        "title": "A",
        "artist": "X",
        "genre": "ambient",
        "fingerprint": {"key": "C", "bpm": 100},
    }
    up_exact = {
        "title": "B",
        "artist": "Y",
        "genre": "rock",
        "fingerprint": {"key": "D", "bpm": 110},
    }
    down_exact = {
        "title": "C",
        "artist": "Z",
        "genre": "jazz",
        "fingerprint": {"key": "E", "bpm": 90},
    }

    dj.generate_segue(prev, up_exact)
    prompt_up = dj.llm_router.generate.call_args[0][0]
    assert "bumping up the energy" not in prompt_up
    assert "slowing things down" not in prompt_up

    dj.generate_segue(prev, down_exact)
    prompt_down = dj.llm_router.generate.call_args[0][0]
    assert "bumping up the energy" not in prompt_down
    assert "slowing things down" not in prompt_down
