"""Successful /request with PLAYER_INSTANCE=None still queues after DJ, logs add_track error."""

import json
import logging
import urllib.error
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


class _RequestDJ:
    def __init__(self):
        self.called = False

    def request_track(self, url: str):
        self.called = True
        return {
            "title": "Queued",
            "artist": "Edge",
            "filename": "queued.wav",
            "url": url,
        }


def _post(url: str, body: dict) -> tuple[int, str]:
    raw = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json", "Content-Length": str(len(raw))},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def test_request_null_player_after_successful_track(tmp_path: Path, caplog):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    dj = _RequestDJ()
    AudioRequestHandler.DJ_INSTANCE = dj
    AudioRequestHandler.PLAYER_INSTANCE = None
    base = f"http://localhost:{server.port}"
    try:
        with caplog.at_level(logging.ERROR, logger="qfzz.streaming.server"):
            code, body = _post(
                f"{base}/request",
                {"url": "https://archive.org/details/demo"},
            )
        assert dj.called is True
        # Client receives 200 JSON first; add_track on None is logged then bare 400 written
        assert code == 200
        assert '"status": "queued"' in body or '"status":"queued"' in body
        assert any("add_track" in r.message for r in caplog.records)
    finally:
        server.stop()
        AudioRequestHandler.PLAYER_INSTANCE = None
