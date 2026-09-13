"""Tests for DatasetManager add/remove/quality scoring."""

from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense


def _make_dataset(dataset_id: str, license_type: str = "CC-BY", tracks=None) -> Dataset:
    if tracks is None:
        tracks = [
            {
                "track_id": f"{dataset_id}-1",
                "title": "Song",
                "artist": "Artist A",
                "genre": "ambient",
                "duration": 180,
                "energy": 0.4,
            },
            {
                "track_id": f"{dataset_id}-2",
                "title": "Song 2",
                "artist": "Artist B",
                "genre": "jazz",
                "duration": 200,
                "energy": 0.6,
            },
        ]
    return Dataset(
        dataset_id=dataset_id,
        name=f"Dataset {dataset_id}",
        description="test",
        version="1.0",
        license=DatasetLicense(
            license_type=license_type,
            license_url="https://example.com/license",
            commercial_use=True,
            derivative_works=True,
            share_alike=False,
        ),
        creator_id="creator",
        tracks=tracks,
    )


class TestDatasetManager:
    def test_reject_incompatible_license(self):
        mgr = DatasetManager(allowed_licenses=["CC0"])
        assert mgr.add_dataset(_make_dataset("ds1", license_type="GPL-3.0")) is False
        assert mgr.get_dataset("ds1") is None

    def test_add_list_remove(self):
        mgr = DatasetManager(allowed_licenses=["CC-BY", "CC0"])
        assert mgr.add_dataset(_make_dataset("ds1")) is True
        assert mgr.add_dataset(_make_dataset("ds2", tracks=[])) is True
        listed = mgr.list_datasets()
        assert len(listed) == 2
        assert listed[0].quality_score >= listed[1].quality_score
        filtered = mgr.list_datasets(min_quality=0.9)
        assert all(d.quality_score >= 0.9 for d in filtered)
        assert mgr.remove_dataset("ds1") is True
        assert mgr.remove_dataset("missing") is False

    def test_quality_score_empty_vs_populated(self):
        mgr = DatasetManager()
        empty = _make_dataset("empty", tracks=[])
        rich = _make_dataset("rich")
        empty_score = mgr.calculate_quality_score(empty)
        rich_score = mgr.calculate_quality_score(rich)
        assert empty_score < rich_score
        assert 0.0 <= empty_score <= 1.0
        assert 0.0 <= rich_score <= 1.0

    def test_validate_license_and_statistics(self):
        mgr = DatasetManager(allowed_licenses=["CC-BY"])
        ds = _make_dataset("ds1")
        assert mgr.validate_license(ds.license) is True
        mgr.add_dataset(ds)
        stats = mgr.get_statistics()
        assert stats["total_datasets"] == 1
        assert stats["total_tracks"] == 2
        assert stats["unique_genres"] >= 1
        assert "CC-BY" in stats["allowed_licenses"]
