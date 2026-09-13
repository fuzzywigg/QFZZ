"""License / metadata / diversity / empty stats edges for DatasetManager."""

import pytest

from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense


def _license(**kwargs) -> DatasetLicense:
    base = dict(
        license_type="CC0",
        license_url="https://example.com/license",
        commercial_use=False,
        derivative_works=False,
        share_alike=True,
    )
    base.update(kwargs)
    return DatasetLicense(**base)


def _dataset(dataset_id: str, tracks, license=None) -> Dataset:
    return Dataset(
        dataset_id=dataset_id,
        name=dataset_id,
        description="t",
        version="1.0",
        license=license or _license(),
        creator_id="c",
        tracks=tracks,
    )


def test_score_license_combinations():
    mgr = DatasetManager()
    restrictive = _license(commercial_use=False, derivative_works=False, share_alike=True)
    permissive = _license(commercial_use=True, derivative_works=True, share_alike=False)
    assert mgr._score_license(restrictive) == 0.5
    assert mgr._score_license(permissive) == pytest.approx(1.0)
    mid = _license(commercial_use=True, derivative_works=False, share_alike=True)
    assert 0.5 < mgr._score_license(mid) < 1.0


def test_score_metadata_partial_required_and_optional():
    mgr = DatasetManager()
    partial = _dataset(
        "partial",
        [
            {
                "title": "T",
                "artist": "A",
                # missing genre + duration
                "album": "Alb",
                "year": 2020,
            }
        ],
    )
    full = _dataset(
        "full",
        [
            {
                "title": "T",
                "artist": "A",
                "genre": "g",
                "duration": 120,
                "album": "Alb",
                "year": 2020,
                "mood": "calm",
                "energy": 0.4,
                "tempo": "slow",
            }
        ],
    )
    assert mgr._score_metadata_completeness(partial) < mgr._score_metadata_completeness(full)
    assert mgr._score_metadata_completeness(full) == 1.0


def test_score_diversity_same_vs_varied():
    mgr = DatasetManager()
    same = _dataset(
        "same",
        [{"title": f"t{i}", "artist": "One", "genre": "rock"} for i in range(10)],
    )
    varied = _dataset(
        "varied",
        [
            {"title": f"t{i}", "artist": f"A{i}", "genre": f"g{i % 12}"}
            for i in range(20)
        ],
    )
    assert mgr._score_diversity(same) < mgr._score_diversity(varied)


def test_get_statistics_empty_manager():
    mgr = DatasetManager()
    stats = mgr.get_statistics()
    assert stats["total_datasets"] == 0
    assert stats["total_tracks"] == 0
    assert stats["average_quality_score"] == 0.0
