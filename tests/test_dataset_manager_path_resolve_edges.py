"""DatasetManager relative filepath resolve / skip missing edges."""

from pathlib import Path

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


def test_build_playlist_relative_filepath_and_absolute_passthrough(tmp_path: Path):
    mgr = DatasetManager(allowed_licenses=["CC0"])
    nested = tmp_path / "deep"
    nested.mkdir()
    rel = nested / "track.wav"
    rel.write_bytes(b"RIFF")
    abs_file = tmp_path / "abs.wav"
    abs_file.write_bytes(b"RIFF")

    ds = Dataset(
        dataset_id="paths",
        name="paths",
        description="t",
        version="1.0",
        license=_license(),
        creator_id="c",
        tracks=[
            {"title": "Rel", "filepath": "deep/track.wav", "duration": 2},
            {"title": "Abs", "filepath": str(abs_file), "duration": 3},
            {"title": "Missing", "filepath": "deep/missing.wav"},
        ],
    )
    ds.quality_score = 0.9
    assert mgr.add_dataset(ds) is True

    playlist = mgr.build_streamable_playlist(str(tmp_path))
    titles = {t["title"] for t in playlist}
    assert titles == {"Rel", "Abs"}
    rel_entry = next(t for t in playlist if t["title"] == "Rel")
    assert rel_entry["filepath"] == str(rel)
    abs_entry = next(t for t in playlist if t["title"] == "Abs")
    assert abs_entry["filepath"] == str(abs_file)
