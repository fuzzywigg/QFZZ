"""TTSClient ElevenLabs/Google init Exception soft-fail edges."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_elevenlabs_getenv_exception_clears_client(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")

    def boom(key, default=None):
        if key == "ELEVENLABS_API_KEY":
            raise RuntimeError("env boom")
        return default

    with patch("qfzz.dj.tts_client.os.getenv", side_effect=boom):
        client = TTSClient(provider="elevenlabs")
    assert client._client is None
    assert client.is_available() is False


def test_google_client_ctor_exception_clears_client():
    fake_tts = MagicMock()
    fake_tts.TextToSpeechClient.side_effect = RuntimeError("creds missing")
    fake_cloud = MagicMock()
    fake_cloud.texttospeech = fake_tts
    fake_google = MagicMock()
    fake_google.cloud = fake_cloud

    with patch.dict(
        "sys.modules",
        {
            "google": fake_google,
            "google.cloud": fake_cloud,
            "google.cloud.texttospeech": fake_tts,
        },
    ):
        client = TTSClient(provider="google")
    assert client._client is None
    assert client.is_available() is False
