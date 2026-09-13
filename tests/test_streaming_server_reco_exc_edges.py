"""StreamingServer /api/dj/recommendations coercion and runtime 500 edges."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _RecoDJ:
    def __init__(self, boom: bool = False):
        self.boom = boom

    def generate_llm_recommendation_response(self, **kwargs):
        if self.boom:
            raise RuntimeError("reco explode")
        return {"recommendations": [], "response": "ok", "used_fallback": False}


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


def test_recommendations_bad_max_tracks_returns_500(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_RecoDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(
            f"{base}/api/dj/recommendations",
            {"user_id": "u", "max_tracks": "not-an-int"},
        )
        assert code == 500
        assert payload.get("error") == "Failed to process recommendation request"
    finally:
        server.stop()


def test_recommendations_generator_exception_returns_500(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_RecoDJ(boom=True), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(
            f"{base}/api/dj/recommendations",
            {"user_id": "u", "message": "vibe"},
        )
        assert code == 500
        assert "Failed to process recommendation" in payload.get("error", "")
    finally:
        server.stop()
