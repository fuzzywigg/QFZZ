"""StreamingServer.start bind-failure soft return."""

from unittest.mock import patch

from qfzz.streaming.server import StreamingServer


def test_start_returns_false_when_bind_raises(tmp_path):
    server = StreamingServer(str(tmp_path), port=0)
    with patch(
        "qfzz.streaming.server.socketserver.TCPServer",
        side_effect=OSError("Address already in use"),
    ):
        assert server.start() is False
        assert server.httpd is None
