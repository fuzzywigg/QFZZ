"""TTS Google NEUTRAL voice when voice_id is omitted."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


def test_google_synthesize_without_voice_id_uses_neutral_ssml_gender():
    fake_tts = MagicMock()
    fake_client = MagicMock()
    fake_client.synthesize_speech.return_value = MagicMock(audio_content=b"neutral-audio")
    voice_calls = []

    def capture_voice(**kw):
        voice_calls.append(kw)
        return kw

    fake_tts.TextToSpeechClient.return_value = fake_client
    fake_tts.SynthesisInput = MagicMock(side_effect=lambda **kw: kw)
    fake_tts.VoiceSelectionParams = MagicMock(side_effect=capture_voice)
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
        audio = client.synthesize("speak neutrally")  # voice_id defaults to None

    assert audio == b"neutral-audio"
    assert voice_calls
    assert voice_calls[0].get("language_code") == "en-US"
    assert voice_calls[0].get("ssml_gender") == "NEUTRAL"
    assert "name" not in voice_calls[0]
