"""StreamingServer defaults missing user_id to anonymous."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _EchoDJ:
    def interact(self, user_id: str, message: str) -> str:
        return f"echo:{user_id}:{message}"

    def generate_llm_recommendation_response(self, **kwargs):
        return {
            "user_id": kwargs.get("user_id"),
            "response": "ok",
            "provider": "Mock",
            "llm_online": False,
            "used_fallback": True,
            "execution_mode": "fallback",
            "recommendations": [],
        }


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


def test_dj_chat_omitted_user_id_becomes_anonymous(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_EchoDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(f"{base}/api/dj/chat", {"message": "hello hive"})
        assert code == 200
        assert payload.get("user_id") == "anonymous"
        assert payload.get("response") == "echo:anonymous:hello hive"
    finally:
        server.stop()


def test_dj_recommendations_omitted_user_id_becomes_anonymous(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_EchoDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(f"{base}/api/dj/recommendations", {"message": "vibe"})
        assert code == 200
        assert payload.get("user_id") == "anonymous"
    finally:
        server.stop()
