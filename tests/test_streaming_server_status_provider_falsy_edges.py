"""Falsy STREAM_STATUS_PROVIDER keeps prior STREAM_STATUS payload."""

import json
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


def _get(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def test_falsy_status_provider_keeps_prior_status(tmp_path: Path):
    AudioRequestHandler.STREAM_STATUS_PROVIDER = None
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    try:
        server.set_stream_status({"state": "prior", "buffer_seconds": 4})
        server.set_stream_status_provider(lambda: None)
        payload = _get(f"http://localhost:{server.port}/stream/session.json")
        assert payload["state"] == "prior"
        assert payload["buffer_seconds"] == 4

        server.set_stream_status_provider(lambda: {})
        payload2 = _get(f"http://localhost:{server.port}/stream/session.json")
        assert payload2["state"] == "prior"
    finally:
        server.stop()
        AudioRequestHandler.STREAM_STATUS_PROVIDER = None
