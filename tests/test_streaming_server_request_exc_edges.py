"""StreamingServer /request raises inside request_track → bare 400."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _RaiseDJ:
    def request_track(self, url: str):
        raise RuntimeError(f"ingest fail: {url}")


def _post(url: str, body: dict) -> tuple[int, bytes]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Content-Length": str(len(data))},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_request_track_exception_returns_400(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_RaiseDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, body = _post(
            f"{base}/request",
            {"url": "https://archive.org/details/demo"},
        )
        assert code == 400
        assert body == b""
    finally:
        server.stop()
