"""Corrupt body / preference type / missing DJ / unknown POST edges for StreamingServer."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


class _FakeDJ:
    def interact(self, user_id: str, message: str) -> str:
        return f"{user_id}:{message}"

    def generate_llm_recommendation_response(self, **kwargs):
        return {"recommendations": [], "response": "ok"}


def _post_raw(url: str, body: bytes, content_type: str = "application/json") -> tuple[int, dict | str]:
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type, "Content-Length": str(len(body))},
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


def test_corrupt_json_and_preferences_type(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_FakeDJ(), None)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post_raw(f"{base}/api/dj/chat", b"{bad")
        assert code == 500
        assert "error" in payload

        code, payload = _post_raw(
            f"{base}/api/dj/recommendations",
            json.dumps({"user_id": "u", "preferences": []}).encode(),
        )
        assert code == 400
        assert "preferences" in payload.get("error", "").lower()
    finally:
        server.stop()


def test_missing_dj_returns_503_and_unknown_post_404(tmp_path: Path):
    AudioRequestHandler.DJ_INSTANCE = None
    AudioRequestHandler.PLAYER_INSTANCE = None
    AudioRequestHandler.STREAM_ERROR_HANDLER = None

    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post_raw(
            f"{base}/api/dj/chat",
            json.dumps({"user_id": "u", "message": "hi"}).encode(),
        )
        assert code == 503

        code, payload = _post_raw(
            f"{base}/api/dj/recommendations",
            json.dumps({"user_id": "u"}).encode(),
        )
        assert code == 503

        code, _ = _post_raw(f"{base}/nope", b"{}")
        assert code == 404

        code, _ = _post_raw(f"{base}/request", b"{}")
        assert code == 400
    finally:
        server.stop()


def test_reconnect_handler_false_returns_503(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.set_stream_error_handler(lambda *_args, **_kwargs: False)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post_raw(f"{base}/stream/reconnect", b"{}")
        assert code == 503
        assert payload.get("recovered") is False
    finally:
        server.stop()
        AudioRequestHandler.STREAM_ERROR_HANDLER = None
