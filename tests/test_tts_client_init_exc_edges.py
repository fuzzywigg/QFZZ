"""TTS Google/ElevenLabs non-Import init failures + synth exception → None."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_google_init_non_import_exception_unavailable():
    fake_tts = MagicMock()
    fake_tts.TextToSpeechClient.side_effect = RuntimeError("adc missing")
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


def test_elevenlabs_init_exception_unavailable(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
    with patch("qfzz.dj.tts_client.os.getenv", side_effect=RuntimeError("env boom")):
        client = TTSClient(provider="elevenlabs")
    assert client._client is None
    assert client.is_available() is False


def test_google_synthesize_exception_returns_none():
    client = object.__new__(TTSClient)
    client.provider = "google"
    client._client = MagicMock()
    with patch.object(client, "_synthesize_google", side_effect=RuntimeError("synth fail")):
        assert client.synthesize("hello") is None
