"""Scoring tier and streamable playlist edge paths for DatasetManager."""

from pathlib import Path

from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense


def _license(license_type: str = "CC0") -> DatasetLicense:
    return DatasetLicense(
        license_type=license_type,
        license_url="https://example.com/license",
        commercial_use=True,
        derivative_works=True,
        share_alike=False,
    )


def _dataset(dataset_id: str, tracks) -> Dataset:
    return Dataset(
        dataset_id=dataset_id,
        name=dataset_id,
        description="t",
        version="1.0",
        license=_license(),
        creator_id="c",
        tracks=tracks,
    )


def test_empty_track_scoring_zeros():
    mgr = DatasetManager()
    empty = _dataset("empty", [])
    assert mgr._score_metadata_completeness(empty) == 0.0
    assert mgr._score_data_consistency(empty) == 0.0
    assert mgr._score_diversity(empty) == 0.0
    assert mgr._score_dataset_size(empty) == 0.0


def test_consistency_penalties_and_size_tiers():
    mgr = DatasetManager()
    bad = _dataset(
        "bad",
        [{"title": "a", "artist": "x", "duration": -1, "energy": 2.0}],
    )
    good = _dataset(
        "good",
        [{"title": "a", "artist": "x", "duration": 100, "energy": 0.5}],
    )
    assert mgr._score_data_consistency(bad) < mgr._score_data_consistency(good)

    for count, expected in (
        (0, 0.0),
        (9, 0.2),
        (49, 0.4),
        (99, 0.6),
        (499, 0.8),
        (500, 1.0),
    ):
        ds = _dataset(f"s{count}", [{"title": str(i)} for i in range(count)])
        assert mgr._score_dataset_size(ds) == expected


def test_build_streamable_playlist_filters(tmp_path: Path):
    mgr = DatasetManager(allowed_licenses=["CC0"])
    existing = tmp_path / "ok.wav"
    existing.write_bytes(b"RIFF")

    ds_ok = _dataset(
        "keep",
        [
            {"title": "Abs", "artist": "A", "filepath": str(existing), "duration": 5},
            {"title": "Rel", "artist": "B", "filename": "ok.wav", "duration": 4},
            {"title": "Missing", "filename": "nope.wav"},
        ],
    )
    ds_other = _dataset(
        "skip-id",
        [{"title": "Other", "filename": "ok.wav", "duration": 3}],
    )
    ds_ok.quality_score = 0.9
    ds_other.quality_score = 0.9
    assert mgr.add_dataset(ds_ok) is True
    assert mgr.add_dataset(ds_other) is True

    tracks = mgr.build_streamable_playlist(
        content_dir=str(tmp_path),
        dataset_ids=["keep"],
        min_quality=0.0,
    )
    assert len(tracks) == 2
    assert all(t["dataset_id"] == "keep" for t in tracks)
    assert all(t["filename"] == "ok.wav" for t in tracks)

    high = mgr.build_streamable_playlist(
        content_dir=str(tmp_path),
        min_quality=0.99,
    )
    assert high == []
