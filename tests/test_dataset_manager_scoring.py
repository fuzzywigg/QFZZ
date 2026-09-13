"""Deepen DatasetManager quality scoring and streamable playlist paths."""

import os

from qfzz.datasets.manager import DatasetManager
from qfzz.datasets.models import Dataset, DatasetLicense


def _license(
    license_type: str = "CC-BY",
    commercial_use: bool = True,
    derivative_works: bool = True,
    share_alike: bool = False,
) -> DatasetLicense:
    return DatasetLicense(
        license_type=license_type,
        license_url="https://example.com/license",
        commercial_use=commercial_use,
        derivative_works=derivative_works,
        share_alike=share_alike,
    )


def _dataset(dataset_id: str, tracks, license_obj=None) -> Dataset:
    return Dataset(
        dataset_id=dataset_id,
        name=f"Dataset {dataset_id}",
        description="test",
        version="1.0",
        license=license_obj or _license(),
        creator_id="creator",
        tracks=tracks,
    )


def _full_track(i: int, genre: str = "ambient", artist: str | None = None) -> dict:
    return {
        "track_id": f"t{i}",
        "title": f"Song {i}",
        "artist": artist or f"Artist {i}",
        "genre": genre,
        "duration": 180 + i,
        "energy": 0.4,
        "album": f"Album {i % 3}",
        "year": 2020,
        "mood": "calm",
        "tempo": "medium",
    }


class TestDatasetManagerScoring:
    def test_size_tiers(self):
        mgr = DatasetManager()
        assert mgr._score_dataset_size(_dataset("empty", [])) == 0.0
        assert mgr._score_dataset_size(_dataset("tiny", [_full_track(i) for i in range(5)])) == 0.2
        assert mgr._score_dataset_size(_dataset("small", [_full_track(i) for i in range(20)])) == 0.4
        assert mgr._score_dataset_size(_dataset("mid", [_full_track(i) for i in range(60)])) == 0.6
        assert mgr._score_dataset_size(_dataset("large", [_full_track(i) for i in range(120)])) == 0.8
        assert mgr._score_dataset_size(_dataset("huge", [_full_track(i) for i in range(500)])) == 1.0

    def test_incomplete_metadata_scores_lower(self):
        mgr = DatasetManager()
        rich = _dataset("rich", [_full_track(0)])
        sparse = _dataset(
            "sparse",
            [{"track_id": "s1", "title": "Only Title"}],
        )
        assert mgr._score_metadata_completeness(sparse) < mgr._score_metadata_completeness(rich)
        assert mgr._score_metadata_completeness(_dataset("empty", [])) == 0.0

    def test_inconsistent_and_invalid_values_lower_consistency(self):
        mgr = DatasetManager()
        consistent = _dataset(
            "ok",
            [
                _full_track(0),
                _full_track(1),
            ],
        )
        inconsistent = _dataset(
            "bad",
            [
                _full_track(0),
                {"title": "Odd", "energy": 2.5, "duration": -5},
            ],
        )
        assert mgr._score_data_consistency(inconsistent) < mgr._score_data_consistency(consistent)
        assert mgr._score_data_consistency(_dataset("empty", [])) == 0.0

    def test_diversity_and_license_scores(self):
        mgr = DatasetManager()
        mono = _dataset("mono", [_full_track(i, genre="rock", artist="Same") for i in range(10)])
        diverse = _dataset(
            "div",
            [_full_track(i, genre=f"g{i}", artist=f"a{i}") for i in range(10)],
        )
        assert mgr._score_diversity(diverse) > mgr._score_diversity(mono)
        assert mgr._score_diversity(_dataset("empty", [])) == 0.0

        permissive = _license(commercial_use=True, derivative_works=True, share_alike=False)
        restrictive = _license(commercial_use=False, derivative_works=False, share_alike=True)
        assert mgr._score_license(permissive) > mgr._score_license(restrictive)

    def test_overall_quality_reflects_richness(self):
        mgr = DatasetManager()
        empty_score = mgr.calculate_quality_score(_dataset("e", []))
        rich_score = mgr.calculate_quality_score(
            _dataset("r", [_full_track(i, genre=f"g{i % 5}") for i in range(30)])
        )
        assert empty_score < rich_score
        assert 0.0 <= empty_score <= 1.0
        assert 0.0 <= rich_score <= 1.0


class TestDatasetManagerPlaylist:
    def test_build_streamable_playlist_resolves_paths_and_filters(self, tmp_path):
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        abs_file = content_dir / "abs.mp3"
        rel_file = content_dir / "rel.mp3"
        named = content_dir / "named.mp3"
        abs_file.write_bytes(b"a")
        rel_file.write_bytes(b"b")
        named.write_bytes(b"c")

        mgr = DatasetManager(allowed_licenses=["CC-BY", "CC0"])
        ds_keep = _dataset(
            "keep",
            [
                {
                    "title": "Abs",
                    "artist": "A",
                    "genre": "ambient",
                    "duration": 10,
                    "filepath": str(abs_file),
                },
                {
                    "title": "Rel",
                    "artist": "B",
                    "genre": "jazz",
                    "duration": 12,
                    "filepath": "rel.mp3",
                },
                {
                    "title": "Named",
                    "artist": "C",
                    "genre": "rock",
                    "duration": 14,
                    "filename": "named.mp3",
                },
                {
                    "title": "Missing",
                    "artist": "D",
                    "genre": "pop",
                    "duration": 16,
                    "filename": "gone.mp3",
                },
            ],
        )
        ds_other = _dataset(
            "other",
            [
                {
                    "title": "Other",
                    "artist": "E",
                    "genre": "folk",
                    "duration": 18,
                    "filename": "named.mp3",
                }
            ],
        )
        assert mgr.add_dataset(ds_keep) is True
        assert mgr.add_dataset(ds_other) is True

        playlist = mgr.build_streamable_playlist(
            str(content_dir), dataset_ids=["keep"], min_quality=0.0
        )
        titles = {t["title"] for t in playlist}
        assert titles == {"Abs", "Rel", "Named"}
        for item in playlist:
            assert os.path.isabs(item["filepath"])
            assert os.path.isfile(item["filepath"])
            assert item["dataset_id"] == "keep"
            assert "dataset_track_index" in item
