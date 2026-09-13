"""Extra blockchain model coverage: qrng mining seed and trust_score edge cases."""

from datetime import datetime
from unittest.mock import MagicMock

from qfzz.blockchain.models import Block, TrustRecord


class TestBlockQrngMining:
    def test_mine_block_uses_qrng_nonce_seed(self):
        block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            records=[],
            previous_hash="0",
        )
        qrng = MagicMock()
        qrng.random_nonce.return_value = 5
        block.mine_block(difficulty=1, qrng=qrng)
        qrng.random_nonce.assert_called_once()
        assert block.hash.startswith("0")
        assert block.nonce >= 5

    def test_mine_block_ignores_qrng_errors(self):
        block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            records=[],
            previous_hash="0",
        )
        qrng = MagicMock()
        qrng.random_nonce.side_effect = RuntimeError("qrng down")
        block.mine_block(difficulty=1, qrng=qrng)
        assert block.hash.startswith("0")
        assert block.nonce >= 0


class TestTrustRecordEdgeCases:
    def test_recalculate_with_zero_total_sets_midpoint(self):
        record = TrustRecord(record_id="r", content_id="c", creator_id="u", trust_score=0.2)
        record.verifications = 0
        record.reports = 0
        record._recalculate_trust_score()
        assert record.trust_score == 0.5

    def test_content_creator_empty_validation(self):
        import pytest

        with pytest.raises(ValueError, match="content_id"):
            TrustRecord(record_id="r", content_id="", creator_id="u", trust_score=0.5)
        with pytest.raises(ValueError, match="creator_id"):
            TrustRecord(record_id="r", content_id="c", creator_id="", trust_score=0.5)
        with pytest.raises(ValueError, match="reports"):
            TrustRecord(
                record_id="r", content_id="c", creator_id="u", trust_score=0.5, reports=-1
            )
