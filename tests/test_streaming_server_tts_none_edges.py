"""DJ chat TTS soft-fail when synthesize_speech returns None."""

import json
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


class _NullTTS:
    def synthesize_speech(self, text: str):
        return None


class _DJ:
    def __init__(self):
        self.ai_dj = _NullTTS()

    def interact(self, user_id: str, message: str) -> str:
        return f"echo:{message}"


def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def test_dj_chat_tts_none_sets_tts_included_false(tmp_path: Path):
    AudioRequestHandler.DJ_INSTANCE = None
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_DJ(), None)
    try:
        payload = _post(
            f"http://localhost:{server.port}/api/dj/chat",
            {"user_id": "u", "message": "hi", "include_tts": True},
        )
        assert payload["response"] == "echo:hi"
        assert payload["tts_included"] is False
        assert "tts_audio_base64" not in payload
    finally:
        server.stop()
        AudioRequestHandler.DJ_INSTANCE = None
