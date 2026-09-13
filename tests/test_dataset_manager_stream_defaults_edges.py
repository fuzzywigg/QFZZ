"""DatasetManager build_streamable_playlist path/default/duration edges."""

from pathlib import Path

from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense


def _license() -> DatasetLicense:
    return DatasetLicense(
        license_type="CC0",
        license_url="https://creativecommons.org/publicdomain/zero/1.0/",
    )


def _dataset(dataset_id: str, tracks: list[dict]) -> Dataset:
    return Dataset(
        dataset_id=dataset_id,
        name=dataset_id,
        description="edge",
        version="1.0",
        license=_license(),
        creator_id="c1",
        tracks=tracks,
    )


def test_relative_filepath_defaults_and_falsy_duration(tmp_path: Path):
    content = tmp_path / "content"
    nested = content / "nested"
    nested.mkdir(parents=True)
    audio = nested / "rel.wav"
    audio.write_bytes(b"RIFF")

    mgr = DatasetManager(allowed_licenses=["CC0"])
    ds = _dataset(
        "defaults",
        [
            {
                # relative filepath (not absolute, not filename-only); duration key absent
                "filepath": "nested/rel.wav",
            },
            {
                "filepath": "nested/rel.wav",
                "title": "",
                "artist": "",
                "genre": "",
                "duration": 0,
            },
        ],
    )
    ds.quality_score = 1.0
    assert mgr.add_dataset(ds) is True
    # None duration is accepted by playlist builder (add_dataset scoring rejects it)
    ds.tracks[0]["duration"] = None

    tracks = mgr.build_streamable_playlist(content_dir=str(content))
    assert len(tracks) == 2
    assert all(t["filename"] == "rel.wav" for t in tracks)
    assert all(t["filepath"].endswith("rel.wav") for t in tracks)
    # missing keys → defaults; present empty strings preserved by .get(); falsy duration → 0
    assert tracks[0]["title"] == "rel.wav"
    assert tracks[0]["artist"] == "Unknown Artist"
    assert tracks[0]["genre"] == "Unknown"
    assert tracks[0]["duration"] == 0
    assert tracks[1]["title"] == ""
    assert tracks[1]["artist"] == ""
    assert tracks[1]["genre"] == ""
    assert tracks[1]["duration"] == 0
    assert tracks[1]["dataset_track_index"] == 1


def test_missing_filepath_and_filename_skipped(tmp_path: Path):
    mgr = DatasetManager(allowed_licenses=["CC0"])
    ds = _dataset("skip", [{"title": "Ghost"}])
    ds.quality_score = 1.0
    assert mgr.add_dataset(ds) is True
    assert mgr.build_streamable_playlist(content_dir=str(tmp_path)) == []
