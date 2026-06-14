from pathlib import Path

from qfzz.datasets import Dataset, DatasetLicense, DatasetManager
from qfzz.streaming.player import MusicPlayer, PlayerState


def _make_dataset(track_filename: str) -> Dataset:
    return Dataset(
        dataset_id="test-dataset",
        name="Test Dataset",
        description="Dataset for streaming tests",
        version="1.0",
        license=DatasetLicense(license_type="CC0", license_url="https://creativecommons.org/publicdomain/zero/1.0/"),
        creator_id="tester",
        tracks=[
            {
                "title": "Track A",
                "artist": "Artist A",
                "genre": "Test",
                "duration": 5,
                "filename": track_filename,
            }
        ],
    )


def test_build_streamable_playlist_filters_missing_files(tmp_path: Path):
    manager = DatasetManager()
    existing = tmp_path / "existing.wav"
    existing.write_bytes(b"audio")
    dataset = _make_dataset(existing.name)
    dataset.add_track({"title": "Missing", "filename": "missing.wav"})

    assert manager.add_dataset(dataset) is True
    playlist = manager.build_streamable_playlist(str(tmp_path))

    assert len(playlist) == 1
    assert playlist[0]["filename"] == existing.name
    assert playlist[0]["dataset_id"] == "test-dataset"


def test_music_player_exposes_stream_status_and_prefetch(tmp_path: Path):
    manager = DatasetManager()
    player = MusicPlayer(
        content_dir=str(tmp_path),
        port=0,
        dataset_manager=manager,
        prefetch_count=2,
        reconnect_max_attempts=2,
    )
    try:
        dataset = _make_dataset("intro.wav")
        dataset.add_track(
            {
                "title": "Track B",
                "artist": "Artist B",
                "genre": "Test",
                "duration": 5,
                "filename": "test_tone.wav",
            }
        )
        assert manager.add_dataset(dataset) is True

        loaded = player.load_playlist_from_datasets(dataset_ids=["test-dataset"])
        assert loaded == 2

        assert player.play() is True
        status = player.get_stream_status()

        assert status["state"] == PlayerState.PLAYING.value
        assert status["current_track"] is not None
        assert status["current_track"]["url"].startswith("http://localhost:")
        assert len(status["prefetch_tracks"]) == 2
        assert status["buffer_seconds"] >= 2
    finally:
        player.stop()
        player.server.stop()


def test_music_player_reconnect_budget(tmp_path: Path):
    player = MusicPlayer(content_dir=str(tmp_path), port=0, reconnect_max_attempts=2)
    try:
        player.load_playlist(
            [
                {
                    "title": "A",
                    "artist": "B",
                    "filename": "intro.wav",
                    "duration": 3,
                }
            ]
        )
        assert player.play() is True

        assert player.report_stream_error("drop-1", recoverable=True) is True
        assert player.report_stream_error("drop-2", recoverable=True) is True
        assert player.report_stream_error("drop-3", recoverable=True) is False
        assert player.get_state() == PlayerState.STOPPED
    finally:
        player.server.stop()
