"""StreamingServer.stop is a no-op when httpd was never started."""

from qfzz.streaming.server import StreamingServer


def test_stop_without_start_is_noop(tmp_path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.httpd is None
    server.stop()  # must not raise
    assert server.httpd is None
