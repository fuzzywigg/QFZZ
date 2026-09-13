"""Extra dataset aggregation and license compatibility edges."""

import pytest

from qfzz.datasets.models import Dataset, DatasetLicense


def _license(**overrides):
    base = {
        "license_type": "CC0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    }
    base.update(overrides)
    return DatasetLicense(**base)


def _dataset(**overrides):
    base = {
        "dataset_id": "ds-edge",
        "name": "Edge Set",
        "description": "edges",
        "version": "0.1",
        "license": _license(),
        "creator_id": "c1",
    }
    base.update(overrides)
    return Dataset(**base)


def test_empty_dataset_aggregates():
    ds = _dataset()
    assert ds.get_track_count() == 0
    assert ds.get_total_duration() == 0
    assert ds.get_genres() == []
    assert ds.get_artists() == []


def test_tracks_without_genre_artist_ignored_in_lists():
    ds = _dataset()
    ds.add_track({"track_id": "t1", "duration": 10})
    ds.add_track({"track_id": "t2", "genre": "ambient", "artist": "Nova", "duration": 20})
    assert ds.get_genres() == ["ambient"]
    assert ds.get_artists() == ["Nova"]
    assert ds.get_total_duration() == 30


def test_quality_score_boundary():
    assert _dataset(quality_score=0.0).quality_score == 0.0
    assert _dataset(quality_score=1.0).quality_score == 1.0
    with pytest.raises(ValueError, match="quality_score"):
        _dataset(quality_score=-0.01)


def test_license_additional_terms_in_dict():
    lic = _license(additional_terms="keep attribution forever", share_alike=True)
    data = lic.to_dict()
    assert data["additional_terms"] == "keep attribution forever"
    assert data["share_alike"] is True
    assert lic.is_compatible_with(["CC0"]) is True
    assert lic.is_compatible_with([]) is False
