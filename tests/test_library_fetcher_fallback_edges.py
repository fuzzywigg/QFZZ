"""ContentFetcher fallback edges: HTML+mp3, GET errors, artist key, title heuristics."""

from unittest.mock import MagicMock, patch

from qfzz.library.fetcher import ContentFetcher


def test_html_content_type_but_mp3_url_downloads(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head = MagicMock()
    head.headers = {"Content-Type": "text/html; charset=utf-8"}
    get = MagicMock()
    get.raise_for_status = MagicMock()
    get.iter_content.return_value = [b"mp3-bytes"]

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                meta = fetcher.fetch_from_url("https://cdn.example/songs/file.mp3")

    assert meta is not None
    assert meta["filename"].startswith("direct_")
    assert (tmp_path / meta["filename"]).read_bytes() == b"mp3-bytes"


def test_html_without_audio_extension_returns_none(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head = MagicMock()
    head.headers = {"Content-Type": "text/html"}

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head) as head_mock:
            meta = fetcher.fetch_from_url("https://example.com/page")
            head_mock.assert_called()

    assert meta is None


def test_direct_get_http_error_returns_none(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head = MagicMock()
    head.headers = {"Content-Type": "audio/mpeg"}
    get = MagicMock()
    get.raise_for_status.side_effect = RuntimeError("404")

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                meta = fetcher.fetch_from_url("https://archive.org/download/x/y.mp3")

    assert meta is None


def test_ytdlp_uses_artist_when_no_uploader(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    ydl = MagicMock()
    ydl.extract_info.return_value = {
        "id": "art1",
        "title": "Solo",
        "artist": "OnlyArtist",
        "duration": 33,
    }
    ydl_cm = MagicMock()
    ydl_cm.__enter__.return_value = ydl
    ydl_cm.__exit__.return_value = False

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", return_value=ydl_cm):
        meta = fetcher.fetch_from_url("https://archive.org/details/solo")

    assert meta["artist"] == "OnlyArtist"
    assert meta["filename"] == "art1.mp3"


def test_title_with_multiple_dashes_splits_first_artist(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head = MagicMock()
    head.headers = {"Content-Type": "audio/mpeg"}
    get = MagicMock()
    get.raise_for_status = MagicMock()
    get.iter_content.return_value = [b"x"]

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                meta = fetcher.fetch_from_url(
                    "https://archive.org/download/x/Artist_-_Title_-_Remix.mp3"
                )

    assert meta["artist"] == "Artist"
    assert "Title" in meta["title"]
    assert "Remix" in meta["title"]


def test_by_keyword_title_artist_heuristic(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head = MagicMock()
    head.headers = {"Content-Type": "audio/mpeg"}
    get = MagicMock()
    get.raise_for_status = MagicMock()
    get.iter_content.return_value = [b"x"]

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                meta = fetcher.fetch_from_url(
                    "https://archive.org/download/x/Moonlight_by_Luna.mp3"
                )

    assert meta["artist"] == "Luna"
    assert "Moonlight" in meta["title"]
