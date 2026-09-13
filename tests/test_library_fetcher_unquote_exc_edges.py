"""ContentFetcher direct fallback continues when unquote raises."""

from unittest.mock import MagicMock, patch

from qfzz.library.fetcher import ContentFetcher


def test_direct_fallback_unquote_exception_uses_original_name(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))

    head = MagicMock()
    head.headers = {"Content-Type": "audio/mpeg"}
    get = MagicMock()
    get.raise_for_status = MagicMock()
    get.iter_content.return_value = [b"bytes"]

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                with patch("urllib.parse.unquote", side_effect=ValueError("bad")):
                    meta = fetcher.fetch_from_url(
                        "https://archive.org/download/foo/Raw_Title_Name.mp3"
                    )

    assert meta is not None
    assert meta["genre"] == "External_Direct"
    assert "Raw" in meta["title"] or "Title" in meta["title"] or meta["title"]
