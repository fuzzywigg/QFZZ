"""ContentFetcher direct fallback strips parenthetical junk from titles."""

from unittest.mock import MagicMock, patch

from qfzz.library.fetcher import ContentFetcher


def test_direct_fallback_strips_original_mix_parenthetical(tmp_path):
    fetcher = ContentFetcher(download_dir=str(tmp_path))
    head = MagicMock()
    head.headers = {"Content-Type": "audio/mpeg"}
    get = MagicMock()
    get.raise_for_status = MagicMock()
    get.iter_content.return_value = [b"mp3"]

    with patch("qfzz.library.fetcher.yt_dlp.YoutubeDL", side_effect=RuntimeError("ydl")):
        with patch("requests.head", return_value=head):
            with patch("requests.get", return_value=get):
                meta = fetcher.fetch_from_url(
                    "https://archive.org/download/x/Song_(Original_Mix).mp3"
                )

    assert meta is not None
    assert meta["title"] == "Song"
    assert "Original" not in meta["title"]
    assert "(" not in meta["title"]
