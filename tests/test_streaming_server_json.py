"""StreamingServer JSON GET endpoints and request queue path."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _FakeDJ:
    def request_track(self, url: str):
        if "fail" in url:
            return None
        return {"title": "Queued", "filename": "q.mp3", "source_url": url}

    def interact(self, user_id: str, message: str) -> str:
        return f"{user_id}:{message}"


class _FakePlayer:
    def __init__(self):
        self.tracks = []

    def add_track(self, track):
        self.tracks.append(track)


def _get(url: str) -> tuple[int, bytes, str]:
    with urllib.request.urlopen(url) as response:
        return response.status, response.read(), response.headers.get_content_type()


def _post(url: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return e.code, parsed


def test_streaming_server_public_json_endpoints(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        status, body, ctype = _get(f"{base}/playlist.json")
        assert status == 200
        assert ctype == "application/json"
        assert isinstance(json.loads(body), (dict, list))

        status, body, _ = _get(f"{base}/graph.json")
        assert status == 200
        assert isinstance(json.loads(body), (dict, list))

        status, body, _ = _get(f"{base}/dj_message.json")
        assert status == 200

        status, body, _ = _get(f"{base}/ledger.json")
        assert status == 200

        status, body, _ = _get(f"{base}/stream/session.json")
        assert status == 200
        session = json.loads(body)
        assert isinstance(session, dict)

        status, body, ctype = _get(f"{base}/stream/manifest.m3u8")
        assert status == 200
        assert b"#EXTM3U" in body
    finally:
        server.stop()


def test_streaming_server_request_queue_and_errors(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    dj = _FakeDJ()
    player = _FakePlayer()
    server.attach_instances(dj, player)
    base = f"http://localhost:{server.port}"
    try:
        code, payload = _post(f"{base}/request", {"url": "https://archive.org/details/ok"})
        assert code == 200
        assert payload["status"] == "queued"
        assert player.tracks[-1]["filename"] == "q.mp3"

        code, _ = _post(f"{base}/request", {"url": "https://example.com/fail"})
        assert code == 400

        code, payload = _post(f"{base}/api/dj/chat", {"user_id": "u", "message": ""})
        assert code == 400
        assert "message" in payload.get("error", "").lower()
    finally:
        server.stop()


def test_streaming_server_reconnect_and_llm_empty(tmp_path: Path):
    from qfzz.streaming.server import AudioRequestHandler

    AudioRequestHandler.STREAM_ERROR_HANDLER = None
    AudioRequestHandler.DJ_INSTANCE = None

    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        # No DJ attached → empty provider status
        status, body, _ = _get(f"{base}/api/llm/providers")
        assert status == 200
        data = json.loads(body)
        assert data["total_providers"] == 0

        code, payload = _post(f"{base}/stream/reconnect", {})
        # Without STREAM_ERROR_HANDLER, expect 503
        assert code == 503
    finally:
        server.stop()
