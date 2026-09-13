"""StreamingServer chat rejects empty message with 400."""

import json
import types
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


def _post(url: str, body: dict) -> tuple[int, dict]:
    data = json.dumps(body).encode()
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


def test_dj_chat_empty_message_returns_400(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(
        types.SimpleNamespace(interact=lambda *_a, **_k: "ok"),
        None,
    )
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(
            f"{base}/api/dj/chat",
            {"user_id": "u1", "message": "   "},
        )
        assert code == 400
        assert "message" in payload.get("error", "").lower()
    finally:
        server.stop()
