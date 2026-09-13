"""TTS ElevenLabs default Rachel voice id when voice_id is None."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_elevenlabs_synthesize_without_voice_id_uses_rachel_default(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
    client = TTSClient(provider="elevenlabs")
    assert client._client is not None

    fake_response = MagicMock()
    fake_response.content = b"rachel-audio"
    fake_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=fake_response) as post:
        audio = client.synthesize("hello there")

    assert audio == b"rachel-audio"
    called_url = post.call_args.args[0]
    assert called_url.endswith("/21m00Tcm4TlvDq8ikWAM")
    assert "xi-api-key" in post.call_args.kwargs["headers"]
