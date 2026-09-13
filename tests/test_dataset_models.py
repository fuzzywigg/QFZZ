"""Tests for dataset models (license + track CRUD)."""

import pytest

from qfzz.datasets.models import Dataset, DatasetLicense, LicenseType


def _license(**overrides) -> DatasetLicense:
    base = {
        "license_type": "CC-BY",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
    }
    base.update(overrides)
    return DatasetLicense(**base)


def _dataset(**overrides) -> Dataset:
    base = {
        "dataset_id": "ds1",
        "name": "Open Beats",
        "description": "demo",
        "version": "1.0",
        "license": _license(),
        "creator_id": "creator-1",
    }
    base.update(overrides)
    return Dataset(**base)


class TestDatasetLicense:
    def test_license_type_enum_values(self):
        assert LicenseType.CC0.value == "CC0"
        assert LicenseType.MIT.value == "MIT"

    def test_is_compatible_with(self):
        lic = _license(license_type="CC0")
        assert lic.is_compatible_with(["CC0", "CC-BY"]) is True
        assert lic.is_compatible_with(["MIT"]) is False

    def test_to_dict(self):
        data = _license(share_alike=True, commercial_use=False).to_dict()
        assert data["license_type"] == "CC-BY"
        assert data["share_alike"] is True
        assert data["commercial_use"] is False


class TestDataset:
    def test_validation_errors(self):
        with pytest.raises(ValueError, match="dataset_id"):
            _dataset(dataset_id="")
        with pytest.raises(ValueError, match="name"):
            _dataset(name="")
        with pytest.raises(ValueError, match="version"):
            _dataset(version="")
        with pytest.raises(ValueError, match="creator_id"):
            _dataset(creator_id="")
        with pytest.raises(ValueError, match="quality_score"):
            _dataset(quality_score=1.5)

    def test_add_remove_track(self):
        ds = _dataset()
        ds.add_track(
            {"track_id": "t1", "title": "A", "artist": "X", "genre": "jazz", "duration": 120}
        )
        ds.add_track(
            {"track_id": "t2", "title": "B", "artist": "Y", "genre": "rock", "duration": 90}
        )
        assert ds.get_track_count() == 2
        assert ds.get_total_duration() == 210
        assert ds.get_genres() == ["jazz", "rock"]
        assert ds.get_artists() == ["X", "Y"]
        assert ds.remove_track("t1") is True
        assert ds.remove_track("missing") is False
        assert ds.get_track_count() == 1

    def test_to_dict_includes_aggregates(self):
        ds = _dataset()
        ds.add_track({"track_id": "t1", "duration": 10})
        data = ds.to_dict()
        assert data["track_count"] == 1
        assert data["total_duration"] == 10
        assert data["license"]["license_type"] == "CC-BY"
