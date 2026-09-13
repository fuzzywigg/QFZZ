"""Dataset model aggregate edges: missing keys, duration default, license enum, remove."""

import time

from qfzz.datasets.models import Dataset, DatasetLicense, LicenseType


def _license() -> DatasetLicense:
    return DatasetLicense(
        license_type=LicenseType.CC0.value,
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        attribution_required=False,
    )


def test_get_genres_artists_ignore_missing_keys():
    ds = Dataset(
        dataset_id="d1",
        name="N",
        description="d",
        version="1",
        license=_license(),
        creator_id="c",
        tracks=[
            {"track_id": "a", "genre": "rock", "artist": "A"},
            {"track_id": "b"},
            {"track_id": "c", "genre": "jazz"},
            {"track_id": "d", "artist": "B"},
        ],
    )
    assert ds.get_genres() == ["jazz", "rock"]
    assert ds.get_artists() == ["A", "B"]


def test_get_total_duration_defaults_missing_to_zero():
    ds = Dataset(
        dataset_id="d2",
        name="N",
        description="d",
        version="1",
        license=_license(),
        creator_id="c",
        tracks=[
            {"track_id": "a", "duration": 10},
            {"track_id": "b"},
            {"track_id": "c", "duration": 5},
        ],
    )
    assert ds.get_total_duration() == 15


def test_license_type_enum_complete():
    values = {m.value for m in LicenseType}
    assert "CC0" in values
    assert "Public-Domain" in values
    assert "Apache-2.0" in values
    assert len(values) == 9


def test_remove_track_updates_updated_at():
    ds = Dataset(
        dataset_id="d3",
        name="N",
        description="d",
        version="1",
        license=_license(),
        creator_id="c",
        tracks=[{"track_id": "keep"}, {"track_id": "drop"}],
    )
    before = ds.updated_at
    time.sleep(0.01)
    assert ds.remove_track("drop") is True
    assert ds.get_track_count() == 1
    assert ds.updated_at >= before
    assert ds.remove_track("missing") is False
