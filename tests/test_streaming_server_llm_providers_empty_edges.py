"""StreamingServer /api/llm/providers returns empty payload when DJ has no router."""

import json
import urllib.request
from pathlib import Path

from qfzz.streaming.server import AudioRequestHandler, StreamingServer


class _BareDJ:
    pass


def test_llm_providers_empty_when_no_router(tmp_path: Path):
    server = StreamingServer(str(tmp_path), port=0)
    assert server.start() is True
    AudioRequestHandler.DJ_INSTANCE = _BareDJ()
    base = f"http://localhost:{server.port}"
    try:
        with urllib.request.urlopen(f"{base}/api/llm/providers") as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
        assert payload["total_providers"] == 0
        assert payload["available_providers"] == []
        assert payload["providers"] == []
    finally:
        server.stop()
