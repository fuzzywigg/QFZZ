"""StreamingServer /api/dj/chat runtime exception → 500 edges."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _BoomDJ:
    def interact(self, user_id: str, message: str) -> str:
        raise RuntimeError(f"chat fail for {user_id}:{message}")


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


def test_dj_chat_interact_exception_returns_500(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_BoomDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(
            f"{base}/api/dj/chat",
            {"user_id": "u1", "message": "hello hive"},
        )
        assert code == 500
        assert payload.get("error") == "Failed to process DJ chat request"
    finally:
        server.stop()
