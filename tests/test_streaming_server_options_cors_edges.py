"""OPTIONS CORS branch inside AudioRequestHandler.end_headers."""

from unittest.mock import MagicMock, patch

from qfzz.streaming.server import AudioRequestHandler


def test_end_headers_options_sends_200_and_cors():
    handler = AudioRequestHandler.__new__(AudioRequestHandler)
    handler.command = "OPTIONS"
    handler.path = "/playlist.json"
    handler.send_header = MagicMock()
    handler.send_response = MagicMock()

    with patch(
        "http.server.SimpleHTTPRequestHandler.end_headers",
        return_value=None,
    ) as super_end:
        AudioRequestHandler.end_headers(handler)

    handler.send_response.assert_called_once_with(200)
    header_names = [c.args[0] for c in handler.send_header.call_args_list]
    assert "Access-Control-Allow-Origin" in header_names
    assert "Access-Control-Allow-Methods" in header_names
    assert "Access-Control-Allow-Headers" in header_names
    super_end.assert_called_once()


def test_end_headers_get_skips_options_response():
    handler = AudioRequestHandler.__new__(AudioRequestHandler)
    handler.command = "GET"
    handler.path = "/playlist.json"
    handler.send_header = MagicMock()
    handler.send_response = MagicMock()

    with patch(
        "http.server.SimpleHTTPRequestHandler.end_headers",
        return_value=None,
    ):
        AudioRequestHandler.end_headers(handler)

    handler.send_response.assert_not_called()
    assert any(
        c.args == ("Cache-Control", "no-store, no-cache, must-revalidate")
        for c in handler.send_header.call_args_list
    )
