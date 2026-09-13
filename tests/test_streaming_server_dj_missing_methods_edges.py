"""StreamingServer DJ present but missing interact/reco methods → 503."""

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


def test_dj_without_interact_or_reco_methods_returns_503(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    # Present instance but lacks interact / generate_llm_recommendation_response
    server.attach_instances(types.SimpleNamespace(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(
            f"{base}/api/dj/chat",
            {"user_id": "u1", "message": "hello"},
        )
        assert code == 503
        assert "not available" in payload.get("error", "").lower()

        code, payload = _post(
            f"{base}/api/dj/recommendations",
            {"user_id": "u1", "message": "suggest"},
        )
        assert code == 503
        assert "recommendation" in payload.get("error", "").lower()
    finally:
        server.stop()
