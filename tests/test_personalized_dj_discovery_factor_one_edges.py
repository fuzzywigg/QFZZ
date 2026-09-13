"""PersonalizedDJ._apply_discovery with discovery_factor=1.0 keeps split_point=1."""

from unittest.mock import patch

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_apply_discovery_factor_one_keeps_single_high_score_slot():
    dj = PersonalizedDJ(enable_ai_dj=False)
    scored = [(1.0 - i * 0.01, {"track_id": f"t{i}"}) for i in range(10)]

    with patch(
        "qfzz.dj.personalized_dj.random.sample",
        side_effect=lambda pool, n: pool[:n],
    ):
        out = dj._apply_discovery(scored, 1.0)

    ids = [t["track_id"] for t in out]
    assert ids[0] == "t0"
    # split_point = max(1, int(10 * 0)) == 1 → discovery pool starts at t1
    assert "t1" in ids
    assert len(out) > 1
