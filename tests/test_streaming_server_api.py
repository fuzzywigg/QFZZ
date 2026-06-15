"""Integration tests for StreamingServer DJ/LLM API endpoints."""

import json
import urllib.request
from pathlib import Path

from qfzz.streaming.server import StreamingServer


class _FakeAI:
    def synthesize_speech(self, text: str) -> bytes:
        return b"voice"


class _FakeLLMRouter:
    def get_status(self):
        return {
            "total_providers": 2,
            "available_providers": ["Ollama", "Mock"],
            "unavailable_providers": [],
            "providers": [{"name": "Ollama", "healthy": True}, {"name": "Mock", "healthy": True}],
        }


class _FakeDJ:
    def __init__(self):
        self.ai_dj = _FakeAI()
        self.llm_router = _FakeLLMRouter()

    def interact(self, user_id: str, message: str) -> str:
        return f"{user_id}:{message}"

    def generate_llm_recommendation_response(
        self, user_id: str, message: str = "", preferences=None, max_tracks: int = 5, include_tts: bool = False
    ):
        payload = {
            "user_id": user_id,
            "response": f"recommend:{message}",
            "provider": "Ollama",
            "llm_online": True,
            "used_fallback": False,
            "execution_mode": "edge-local",
            "recommendations": [{"title": "Orbit"}][:max_tracks],
        }
        if include_tts:
            payload["tts_included"] = True
            payload["tts_audio_base64"] = "dm9pY2U="
            payload["tts_format"] = "mp3"
        return payload


class _FakePlayer:
    def add_track(self, track):
        return None


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def test_streaming_server_dj_chat_and_tts_api(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_FakeDJ(), _FakePlayer())
    base_url = f"http://localhost:{server.port}"

    try:
        payload = _post_json(
            f"{base_url}/api/dj/chat",
            {"user_id": "u1", "message": "hello", "include_tts": True},
        )
        assert payload["response"] == "u1:hello"
        assert payload["tts_included"] is True
        assert payload["tts_audio_base64"] == "dm9pY2U="
    finally:
        server.stop()


def test_streaming_server_dj_recommendations_api(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_FakeDJ(), _FakePlayer())
    base_url = f"http://localhost:{server.port}"

    try:
        payload = _post_json(
            f"{base_url}/api/dj/recommendations",
            {"user_id": "u2", "message": "electronic", "max_tracks": 1, "include_tts": True},
        )
        assert payload["provider"] == "Ollama"
        assert payload["execution_mode"] == "edge-local"
        assert len(payload["recommendations"]) == 1
        assert payload["tts_included"] is True
    finally:
        server.stop()


def test_streaming_server_llm_provider_status_api(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    server.attach_instances(_FakeDJ(), _FakePlayer())
    base_url = f"http://localhost:{server.port}"

    try:
        payload = _get_json(f"{base_url}/api/llm/providers")
        assert payload["total_providers"] == 2
        assert "Ollama" in payload["available_providers"]
    finally:
        server.stop()
