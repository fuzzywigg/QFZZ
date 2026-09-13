"""Tests for qfzz.dj.tts_client.TTSClient (mocked providers, no network)."""

from unittest.mock import MagicMock, patch

from qfzz.dj.tts_client import TTSClient


class TestTTSClientAvailability:
    def test_openai_unavailable_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            client = TTSClient(provider="openai")
            assert client.is_available() is False
            assert client.synthesize("hello") is None

    def test_empty_text_returns_none(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        fake_openai = MagicMock()
        fake_openai.OpenAI.return_value = MagicMock()
        with patch.dict("sys.modules", {"openai": fake_openai}):
            client = TTSClient(provider="openai")
            assert client.synthesize("") is None
            assert client.synthesize("   ") is None

    def test_unknown_provider_falls_back_to_openai(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            client = TTSClient(provider="not-a-real-provider")
            assert client.provider == "openai"


class TestTTSClientVoices:
    def test_openai_voices(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            client = TTSClient(provider="openai")
            voices = client.get_available_voices()
            assert "alloy" in voices
            assert "nova" in voices

    def test_elevenlabs_voices(self, monkeypatch):
        monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
        client = TTSClient(provider="elevenlabs")
        assert client.is_available() is True
        assert client.get_available_voices() == ["21m00Tcm4TlvDq8ikWAM"]

    def test_google_voices_list(self):
        client = object.__new__(TTSClient)
        client.provider = "google"
        client._client = None
        assert client.get_available_voices() == [
            "en-US-Neural2-C",
            "en-US-Neural2-D",
        ]

    def test_unknown_provider_voices_empty(self):
        client = object.__new__(TTSClient)
        client.provider = "mystery"
        assert client.get_available_voices() == []


class TestTTSClientSynthesize:
    def test_openai_synthesize_success(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mock_client = MagicMock()
        mock_client.audio.speech.create.return_value = MagicMock(content=b"mp3-bytes")
        fake_openai = MagicMock()
        fake_openai.OpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": fake_openai}):
            client = TTSClient(provider="openai")
            audio = client.synthesize("Welcome to QFZZ", voice_id="echo")
            assert audio == b"mp3-bytes"
            mock_client.audio.speech.create.assert_called_once()
            kwargs = mock_client.audio.speech.create.call_args.kwargs
            assert kwargs["voice"] == "echo"
            assert kwargs["input"] == "Welcome to QFZZ"

    def test_elevenlabs_synthesize_success(self, monkeypatch):
        monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
        client = TTSClient(provider="elevenlabs")

        mock_resp = MagicMock()
        mock_resp.content = b"eleven-audio"
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp) as post:
            audio = client.synthesize("Hello hive")
            assert audio == b"eleven-audio"
            assert post.called
            url = post.call_args[0][0]
            assert "text-to-speech" in url
            headers = post.call_args.kwargs["headers"]
            assert headers["xi-api-key"] == "el-test"

    def test_elevenlabs_http_error_returns_none(self, monkeypatch):
        monkeypatch.setenv("ELEVENLABS_API_KEY", "el-test")
        client = TTSClient(provider="elevenlabs")

        import requests

        with patch(
            "requests.post",
            side_effect=requests.exceptions.RequestException("boom"),
        ):
            assert client.synthesize("fail me") is None

    def test_google_synthesize_success(self):
        fake_tts = MagicMock()
        fake_client = MagicMock()
        fake_client.synthesize_speech.return_value = MagicMock(audio_content=b"g-audio")
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
            assert client.is_available() is True
            audio = client.synthesize("google voice", voice_id="en-US-Neural2-C")
            assert audio == b"g-audio"

    def test_synthesize_without_client_returns_none(self):
        client = object.__new__(TTSClient)
        client.provider = "openai"
        client._client = None
        assert client.synthesize("hi") is None
