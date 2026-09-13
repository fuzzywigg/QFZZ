"""StreamingServer CORS, empty body, TTS-null, and start-fail edges."""

import json
import types
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


class _DJWithNullTTS:
    def __init__(self):
        self.ai_dj = types.SimpleNamespace(synthesize_speech=lambda _text: None)

    def interact(self, user_id: str, message: str) -> str:
        return f"echo:{message}"


def _request(
    url: str,
    method: str = "GET",
    body: bytes | None = None,
    *,
    parse_json: bool = True,
) -> tuple[int, dict | bytes, dict]:
    headers = {}
    data = body
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(body))
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            raw_bytes = response.read()
            hdrs = dict(response.headers)
            if not parse_json:
                return response.status, raw_bytes, hdrs
            raw = raw_bytes.decode("utf-8")
            payload = json.loads(raw) if raw else {}
            return response.status, payload, hdrs
    except urllib.error.HTTPError as e:
        raw_bytes = e.read()
        hdrs = dict(e.headers)
        if not parse_json:
            return e.code, raw_bytes, hdrs
        raw = raw_bytes.decode("utf-8")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return e.code, payload, hdrs


def test_cors_headers_on_json_and_empty_chat_body(tmp_path: Path):
    AudioRequestHandler.LEDGER_STATS = {"height": 0, "status": "Waiting"}
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_DJWithNullTTS(), None)
    server.set_ledger_stats({"height": 7, "status": "ok"})
    base = f"http://localhost:{server.port}"
    try:
        code, payload, headers = _request(f"{base}/ledger.json")
        assert code == 200
        assert headers.get("Access-Control-Allow-Origin") == "*"
        allow = headers.get("Access-Control-Allow-Methods", "")
        assert "GET" in allow and "POST" in allow
        cache = headers.get("Cache-Control", "")
        assert "no-store" in cache
        assert payload["height"] == 7

        # Content-Length 0 / empty body → _read_json_body returns {}
        code, payload, _ = _request(f"{base}/api/dj/chat", method="POST", body=b"")
        assert code == 400
        assert "message" in payload.get("error", "").lower()
    finally:
        server.stop()


def test_dj_chat_tts_none_sets_tts_included_false(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_DJWithNullTTS(), None)
    base = f"http://localhost:{server.port}"
    try:
        body = json.dumps(
            {"user_id": "u1", "message": "hello hive", "include_tts": True}
        ).encode()
        code, payload, _ = _request(f"{base}/api/dj/chat", method="POST", body=body)
        assert code == 200
        assert payload["response"] == "echo:hello hive"
        assert payload["tts_included"] is False
        assert "tts_audio_base64" not in payload
    finally:
        server.stop()


def test_start_returns_false_when_bind_fails(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    with patch("qfzz.streaming.server.socketserver.TCPServer", side_effect=OSError("bind")):
        assert server.start() is False
    assert server.httpd is None


def test_audio_extension_gets_cache_control_public(tmp_path: Path):
    wav = tmp_path / "tone.wav"
    wav.write_bytes(b"RIFF....WAVE")
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    AudioRequestHandler.DJ_INSTANCE = None
    base = f"http://localhost:{server.port}"
    try:
        code, payload, headers = _request(f"{base}/tone.wav", parse_json=False)
        assert code == 200
        assert isinstance(payload, (bytes, bytearray))
        assert payload.startswith(b"RIFF")
        cache = headers.get("Cache-Control", "")
        assert "max-age=300" in cache
        assert headers.get("Accept-Ranges") == "bytes"
    finally:
        server.stop()
