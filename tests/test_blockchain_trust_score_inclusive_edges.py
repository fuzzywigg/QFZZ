"""TrustRecord inclusive trust_score bounds."""

import pytest

from qfzz.blockchain.models import TrustRecord


def test_trust_score_inclusive_zero_and_one_accepted():
    zero = TrustRecord(record_id="r0", content_id="c", creator_id="u", trust_score=0.0)
    one = TrustRecord(record_id="r1", content_id="c", creator_id="u", trust_score=1.0)
    assert zero.trust_score == 0.0
    assert one.trust_score == 1.0


@pytest.mark.parametrize("score", [-0.0001, 1.0001])
def test_trust_score_outside_inclusive_bounds_rejected(score):
    with pytest.raises(ValueError, match="trust_score"):
        TrustRecord(record_id="r", content_id="c", creator_id="u", trust_score=score)
