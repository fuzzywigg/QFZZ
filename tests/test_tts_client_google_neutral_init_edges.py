"""TTS Google NEUTRAL voice path + non-Import init failures."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_google_synthesize_without_voice_id_uses_neutral():
    fake_tts = MagicMock()
    fake_client = MagicMock()
    fake_client.synthesize_speech.return_value = MagicMock(audio_content=b"neutral-mp3")
    fake_tts.TextToSpeechClient.return_value = fake_client
    fake_tts.SynthesisInput = MagicMock(side_effect=lambda **kw: kw)
    fake_tts.VoiceSelectionParams = MagicMock(side_effect=lambda **kw: kw)
    fake_tts.AudioConfig = MagicMock(side_effect=lambda **kw: kw)
    fake_tts.AudioEncoding = MagicMock(MP3="MP3")
    fake_tts.SsmlVoiceGender = MagicMock(NEUTRAL="NEUTRAL")

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
        audio = client.synthesize("hello neutral", voice_id=None)

    assert audio == b"neutral-mp3"
    kwargs = fake_tts.VoiceSelectionParams.call_args.kwargs
    assert kwargs.get("ssml_gender") == "NEUTRAL"
    assert "name" not in kwargs
    assert kwargs.get("language_code") == "en-US"


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
