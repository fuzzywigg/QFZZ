"""Tests for qfzz.library.fetcher.ContentFetcher (mocked yt-dlp / requests)."""

from unittest.mock import MagicMock, patch

from qfzz.library.fetcher import ContentFetcher


class TestContentFetcher:
    def test_creates_download_dir(self, tmp_path):
        target = tmp_path / "dl"
        fetcher = ContentFetcher(download_dir=str(target))
        assert target.exists()
        assert fetcher.download_dir == str(target)

    def test_yt_dlp_verified_domain_success(self, tmp_path):
        fetcher = ContentFetcher(download_dir=str(tmp_path))
        ydl = MagicMock()
        ydl.extract_info.return_value = {
            "id": "abc123",
            "title": "Public Domain Jazz",
            "uploader": "Archive User",
            "duration": 120,
        }
        ydl_cm = MagicMock()
        ydl_cm.__enter__.return_value = ydl
        ydl_cm.__exit__.return_value = False

        with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", return_value=ydl_cm):
            meta = fetcher.fetch_from_url("https://archive.org/details/demo")

        assert meta is not None
        assert meta["title"] == "Public Domain Jazz"
        assert meta["artist"] == "Archive User"
        assert meta["filename"] == "abc123.mp3"
        assert meta["genre"] == "External"
        assert meta["duration"] == 120
        assert meta["source_url"].startswith("https://archive.org")

    def test_yt_dlp_unverified_marks_genre(self, tmp_path):
        fetcher = ContentFetcher(download_dir=str(tmp_path))
        ydl = MagicMock()
        ydl.extract_info.return_value = {
            "id": "xyz",
            "title": "Mystery",
            "artist": "Someone",
            "duration": 10,
        }
        ydl_cm = MagicMock()
        ydl_cm.__enter__.return_value = ydl
        ydl_cm.__exit__.return_value = False

        with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", return_value=ydl_cm):
            meta = fetcher.fetch_from_url("https://example.com/track")

        assert meta["genre"] == "External_Unverified"

    def test_direct_download_fallback_mp3(self, tmp_path):
        fetcher = ContentFetcher(download_dir=str(tmp_path))

        head = MagicMock()
        head.headers = {"Content-Type": "audio/mpeg"}
        get = MagicMock()
        get.raise_for_status = MagicMock()
        get.iter_content.return_value = [b"audio-bytes"]

        with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl fail")):
            with patch("requests.head", return_value=head):
                with patch("requests.get", return_value=get):
                    meta = fetcher.fetch_from_url(
                        "https://archive.org/download/foo/Artist_-_Cool_Track_(Original_Mix).mp3"
                    )

        assert meta is not None
        assert meta["genre"] == "External_Direct"
        assert meta["artist"] == "Artist"
        assert "Cool Track" in meta["title"]
        assert meta["filename"].startswith("direct_")
        saved = tmp_path / meta["filename"]
        assert saved.exists()
        assert saved.read_bytes() == b"audio-bytes"

    def test_html_fallback_returns_none(self, tmp_path):
        fetcher = ContentFetcher(download_dir=str(tmp_path))
        head = MagicMock()
        head.headers = {"Content-Type": "text/html; charset=utf-8"}

        with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("fail")):
            with patch("requests.head", return_value=head):
                meta = fetcher.fetch_from_url("https://example.com/page")

        assert meta is None

    def test_both_paths_fail_returns_none(self, tmp_path):
        fetcher = ContentFetcher(download_dir=str(tmp_path))
        with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("fail")):
            with patch("requests.head", side_effect=OSError("offline")):
                assert fetcher.fetch_from_url("https://example.com/x.mp3") is None

    def test_direct_by_heuristic(self, tmp_path):
        fetcher = ContentFetcher(download_dir=str(tmp_path))
        head = MagicMock()
        head.headers = {"Content-Type": "audio/mpeg"}
        get = MagicMock()
        get.raise_for_status = MagicMock()
        get.iter_content.return_value = [b"x"]

        with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("fail")):
            with patch("requests.head", return_value=head):
                with patch("requests.get", return_value=get):
                    meta = fetcher.fetch_from_url(
                        "https://example.com/files/Song%20Title%20by%20Cool%20Artist.mp3"
                    )

        assert meta is not None
        assert meta["genre"] == "External_Direct_Unverified"
        assert meta["title"] == "Song Title"
        assert meta["artist"] == "Cool Artist"
