"""TTSClient Google ctor Exception (not ImportError) soft-clears client."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_google_ctor_exception_clears_client():
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
