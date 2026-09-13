"""StreamingServer JSON array body on DJ chat → AttributeError → JSON 500."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _ChatDJ:
    def interact(self, user_id: str, message: str) -> str:
        return f"{user_id}:{message}"


def _post_raw(url: str, body: bytes) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
            try:
                return response.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return response.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return e.code, raw


def test_chat_json_array_body_returns_500(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_ChatDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post_raw(f"{base}/api/dj/chat", b"[]")
        assert code == 500
        assert isinstance(payload, dict)
        assert "chat" in payload.get("error", "").lower()
    finally:
        server.stop()
