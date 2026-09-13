"""DatasetManager field-schema inconsistency scoring edges."""

from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense


def _license() -> DatasetLicense:
    return DatasetLicense(
        license_type="CC0",
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


def test_mismatched_field_keys_lower_consistency_than_uniform_schema():
    mgr = DatasetManager()
    uniform = _dataset(
        "uniform",
        [
            {"title": "A", "artist": "X", "genre": "ambient", "duration": 100, "energy": 0.4},
            {"title": "B", "artist": "Y", "genre": "ambient", "duration": 120, "energy": 0.5},
        ],
    )
    mismatched = _dataset(
        "mismatch",
        [
            {"title": "A", "artist": "X", "genre": "ambient", "duration": 100, "energy": 0.4},
            {"title": "B"},  # missing artist/genre/duration/energy keys
        ],
    )
    assert mgr._score_data_consistency(mismatched) < mgr._score_data_consistency(uniform)
    # both tracks have valid duration/energy where present; mismatch is schema overlap
    assert 0.0 < mgr._score_data_consistency(mismatched) < 1.0
