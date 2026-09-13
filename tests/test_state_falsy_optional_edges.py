"""StateManager falsy optional genre/duration omission edges."""

from qfzz.core.state import StateManager


def test_empty_genre_and_zero_duration_omitted(temp_honeycomb):
    sm = StateManager(honeycomb_dir=temp_honeycomb)
    sm.set_current_track(
        track_id="t1",
        title="Pulse",
        artist="Qubit",
        genre="",
        duration=0,
    )
    track = sm._read_file(sm.honeycomb_dir / "current_track.json")
    assert track["track_id"] == "t1"
    assert track["title"] == "Pulse"
    assert "genre" not in track
    assert "duration" not in track
    assert "started_at" in track


def test_none_optional_fields_omitted(temp_honeycomb):
    sm = StateManager(honeycomb_dir=temp_honeycomb)
    sm.set_current_track(track_id="t2", title="Solo", artist="Anon")
    track = sm._read_file(sm.honeycomb_dir / "current_track.json")
    assert "genre" not in track
    assert "duration" not in track


def test_reinit_does_not_overwrite_existing_files(temp_honeycomb):
    sm = StateManager(honeycomb_dir=temp_honeycomb)
    sm.set_current_track(track_id="keep", title="Keep", artist="Me", genre="ambient")
    # Second manager on same dir should not wipe existing current_track.json
    sm2 = StateManager(honeycomb_dir=temp_honeycomb)
    track = sm2._read_file(sm2.honeycomb_dir / "current_track.json")
    assert track["track_id"] == "keep"
    assert track["genre"] == "ambient"
