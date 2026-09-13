"""Dataset quality_score inclusive bound edges."""

import pytest

from qfzz.datasets.models import Dataset, DatasetLicense


def _dataset(**overrides) -> Dataset:
    base = {
        "dataset_id": "ds1",
        "name": "Open Beats",
        "description": "demo",
        "version": "1.0",
        "license": DatasetLicense(
            license_type="CC-BY",
            license_url="https://creativecommons.org/licenses/by/4.0/",
        ),
        "creator_id": "creator-1",
    }
    base.update(overrides)
    return Dataset(**base)


def test_quality_score_inclusive_zero_and_one():
    assert _dataset(quality_score=0.0).quality_score == 0.0
    assert _dataset(quality_score=1.0).quality_score == 1.0


@pytest.mark.parametrize("score", [-0.0001, 1.0001])
def test_quality_score_outside_inclusive_bounds_rejected(score):
    with pytest.raises(ValueError, match="quality_score"):
        _dataset(quality_score=score)
