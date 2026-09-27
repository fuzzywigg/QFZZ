"""ContentFetcher unquote failure and underscore-title cleanup edges."""

from unittest.mock import MagicMock, patch

from qfzz.library.fetcher import ContentFetcher


def _direct_download_mocks(body: bytes = b"x"):
    head = MagicMock()
    head.headers = {"Content-Type": "audio/mpeg"}
    get = MagicMock()
    get.raise_for_status = MagicMock()
    get.iter_content.return_value = [body]
    return head, get


def test_unquote_exception_keeps_original_basename(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head, get = _direct_download_mocks()

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("urllib.parse.unquote", side_effect=RuntimeError("bad pct")):
            with patch("requests.head", return_value=head):
                with patch("requests.get", return_value=get):
                    meta = fetcher.fetch_from_url(
                        "https://archive.org/download/x/Solo_Track.mp3"
                    )

    assert meta is not None
    assert "Solo" in meta["title"]
    assert meta["artist"] == "Unknown Artist"


def test_underscore_title_cleanup_without_artist_split(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head, get = _direct_download_mocks()

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                meta = fetcher.fetch_from_url(
                    "https://archive.org/download/x/Deep_House_Groove.mp3"
                )

    assert meta["artist"] == "Unknown Artist"
    assert " " in meta["title"]
    assert "_" not in meta["title"]
