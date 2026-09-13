"""StreamingServer non-integer Content-Length header edges."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _OkDJ:
    def interact(self, user_id: str, message: str) -> str:
        return "ok"

    def request_track(self, url: str):
        return {"title": "x", "url": url}


def _post_raw(url: str, body: bytes, content_length: str) -> tuple[int, bytes]:
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Content-Length": content_length},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_request_non_int_content_length_returns_bare_400(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_OkDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, raw = _post_raw(
            f"{base}/request",
            json.dumps({"url": "https://archive.org/details/x"}).encode(),
            "abc",
        )
        assert code == 400
        assert raw == b""
    finally:
        server.stop()


def test_dj_chat_non_int_content_length_returns_json_500(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_OkDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, raw = _post_raw(
            f"{base}/api/dj/chat",
            json.dumps({"message": "hi"}).encode(),
            "abc",
        )
        assert code == 500
        payload = json.loads(raw.decode())
        assert payload.get("error") == "Failed to process DJ chat request"
    finally:
        server.stop()
