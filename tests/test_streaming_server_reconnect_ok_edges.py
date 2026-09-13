"""StreamingServer /stream/reconnect recovered=True → 200 edges."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


def _post(url: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Content-Length": str(len(data))},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def test_reconnect_handler_true_returns_200(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.set_stream_error_handler(lambda *_args, **_kwargs: True)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(f"{base}/stream/reconnect")
        assert code == 200
        assert payload.get("recovered") is True
    finally:
        server.stop()
        AudioRequestHandler.STREAM_ERROR_HANDLER = None
