"""StreamingServer /api/dj/recommendations allows JSON null preferences."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _RecoDJ:
    def __init__(self):
        self.last_preferences = "unset"

    def generate_llm_recommendation_response(self, **kwargs):
        self.last_preferences = kwargs.get("preferences", "missing")
        return {"recommendations": [], "response": "ok"}


def _post(url: str, body: dict) -> tuple[int, dict]:
    raw = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json", "Content-Length": str(len(raw))},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")


def test_recommendations_null_preferences_allowed(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    dj = _RecoDJ()
    server.attach_instances(dj, None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(
            f"{base}/api/dj/recommendations",
            {"user_id": "u1", "preferences": None},
        )
        assert code == 200
        assert payload.get("response") == "ok"
        assert dj.last_preferences is None
    finally:
        server.stop()
