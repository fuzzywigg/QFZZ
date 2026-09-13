"""StreamingServer setter / provider / cache-header edge coverage."""

import json
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


def _get(url: str) -> tuple[int, str, dict]:
    try:
        with urllib.request.urlopen(url) as response:
            headers = {k.lower(): v for k, v in response.headers.items()}
            return response.status, response.read().decode("utf-8"), headers
    except urllib.error.HTTPError as e:
        headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        return e.code, e.read().decode("utf-8"), headers


def _reset_handler_state():
    AudioRequestHandler.PAYLOAD = []
    AudioRequestHandler.GRAPH_PAYLOAD = {}
    AudioRequestHandler.DJ_MESSAGE = {"message": ""}
    AudioRequestHandler.LEDGER_STATS = {}
    AudioRequestHandler.STREAM_STATUS = {}
    AudioRequestHandler.STREAM_STATUS_PROVIDER = None
    AudioRequestHandler.STREAM_MANIFEST_PROVIDER = None
    AudioRequestHandler.STREAM_ERROR_HANDLER = None
    AudioRequestHandler.DJ_INSTANCE = None
    AudioRequestHandler.PLAYER_INSTANCE = None


def test_setters_reflected_on_json_endpoints(tmp_path: Path):
    _reset_handler_state()
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        server.set_playlist([{"title": "P1"}])
        server.set_graph({"nodes": [{"id": "n1"}], "links": []})
        server.set_dj_message("hello hive")
        server.set_ledger_stats({"height": 7, "status": "ok"})
        server.set_stream_status({"state": "idle"})

        code, body, _ = _get(f"{base}/playlist.json")
        assert code == 200
        assert json.loads(body)[0]["title"] == "P1"

        code, body, _ = _get(f"{base}/graph.json")
        assert code == 200
        assert json.loads(body)["nodes"][0]["id"] == "n1"

        code, body, _ = _get(f"{base}/dj_message.json")
        assert code == 200
        assert json.loads(body)["message"] == "hello hive"

        code, body, _ = _get(f"{base}/ledger.json")
        assert code == 200
        assert json.loads(body)["height"] == 7

        code, body, _ = _get(f"{base}/stream/session.json")
        assert code == 200
        assert json.loads(body)["state"] == "idle"
    finally:
        server.stop()
        _reset_handler_state()


def test_stream_status_and_manifest_providers(tmp_path: Path):
    _reset_handler_state()
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        server.set_stream_status_provider(lambda: {"state": "live", "buffer_seconds": 9})
        server.set_stream_manifest_provider(
            lambda: "#EXTM3U\n#EXT-X-VERSION:3\n"
        )

        code, body, _ = _get(f"{base}/stream/session.json")
        assert code == 200
        payload = json.loads(body)
        assert payload["state"] == "live"
        assert payload["buffer_seconds"] == 9

        code, body, headers = _get(f"{base}/stream/manifest.m3u8")
        assert code == 200
        assert "#EXTM3U" in body
        assert "no-store" in headers.get("cache-control", "")
    finally:
        server.stop()
        _reset_handler_state()


def test_audio_vs_json_cache_headers(tmp_path: Path):
    _reset_handler_state()
    mp3 = tmp_path / "clip.mp3"
    mp3.write_bytes(b"ID3fake")
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        server.set_playlist([])
        code, _, headers = _get(f"{base}/playlist.json")
        assert code == 200
        assert "no-store" in headers.get("cache-control", "")

        code, _, headers = _get(f"{base}/clip.mp3")
        assert code == 200
        assert "max-age=300" in headers.get("cache-control", "")
        assert headers.get("accept-ranges") == "bytes"
    finally:
        server.stop()
        _reset_handler_state()


def test_llm_providers_endpoint_with_and_without_dj(tmp_path: Path):
    _reset_handler_state()
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    base = f"http://localhost:{server.port}"
    try:
        code, body, _ = _get(f"{base}/api/llm/providers")
        assert code == 200
        empty = json.loads(body)
        assert empty["total_providers"] == 0
        assert empty["providers"] == []

        class _Router:
            def get_status(self):
                return {"providers": ["ollama"], "healthy": True}

        class _DJ:
            llm_router = _Router()

        server.attach_instances(_DJ(), None)
        code, body, _ = _get(f"{base}/api/llm/providers")
        assert code == 200
        payload = json.loads(body)
        assert payload["providers"] == ["ollama"]
        assert payload["healthy"] is True
    finally:
        server.stop()
        _reset_handler_state()
