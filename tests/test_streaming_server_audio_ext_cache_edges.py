"""AudioRequestHandler caches .flac / .aac / .m4a the same as .wav/.mp3."""

from unittest.mock import MagicMock, patch

from qfzz.streaming.server import AudioRequestHandler


def test_flac_aac_m4a_get_public_cache_and_ranges():
    for path in ("/clip.flac", "/clip.aac", "/clip.m4a", "/Clip.FLAC"):
        handler = AudioRequestHandler.__new__(AudioRequestHandler)
        handler.command = "GET"
        handler.path = path
        handler.send_header = MagicMock()
        handler.send_response = MagicMock()

        with patch(
            "http.server.SimpleHTTPRequestHandler.end_headers",
            return_value=None,
        ):
            AudioRequestHandler.end_headers(handler)

        assert any(
            c.args == ("Cache-Control", "public, max-age=300")
            for c in handler.send_header.call_args_list
        )
        assert any(
            c.args == ("Accept-Ranges", "bytes")
            for c in handler.send_header.call_args_list
        )
