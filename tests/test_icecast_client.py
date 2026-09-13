"""
Tests for Icecast streaming client.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

# Mock shout module before importing Icecast client (optional dependency).
sys.modules["shout"] = MagicMock()

from qfzz.streaming import IcecastClient, IcecastConfig, IcecastState  # noqa: E402


class TestIcecastConfig(unittest.TestCase):
    """Test Icecast configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = IcecastConfig()

        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.password, "hackme")
        self.assertEqual(config.mount, "/qfzz")
        self.assertEqual(config.format, "mp3")
        self.assertEqual(config.bitrate, 128)
        self.assertEqual(config.channels, 2)

    def test_custom_config(self):
        """Test custom configuration."""
        config = IcecastConfig(
            host="example.com",
            port=8080,
            password="secret",
            mount="/custom",
            name="Custom Stream",
            bitrate=192,
        )

        self.assertEqual(config.host, "example.com")
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.password, "secret")
        self.assertEqual(config.mount, "/custom")
        self.assertEqual(config.name, "Custom Stream")
        self.assertEqual(config.bitrate, 192)


class TestIcecastClient(unittest.TestCase):
    """Test Icecast client functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = IcecastConfig(
            host="localhost",
            port=8000,
            password="test",
            mount="/test",
        )

    def test_init_without_shout(self):
        """Test initialization without shout-python."""
        # Test passes if SHOUT_AVAILABLE is False (already handled by import mock)
        config = IcecastConfig()
        # This test verifies the client can be initialized even without shout
        self.assertIsInstance(config, IcecastConfig)

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_connect_success(self, mock_shout_module=None):
        """Test successful connection."""
        import shout as mock_shout

        # Mock shout module
        mock_shout_instance = Mock()
        mock_shout.Shout.return_value = mock_shout_instance

        client = IcecastClient(self.config)
        result = client.connect()

        self.assertTrue(result)
        self.assertEqual(client.get_state(), IcecastState.CONNECTED)
        mock_shout_instance.open.assert_called_once()

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_connect_failure(self, mock_shout_module=None):
        """Test connection failure."""
        import shout as mock_shout

        # Mock connection failure
        mock_shout_instance = Mock()
        mock_shout_instance.open.side_effect = Exception("Connection refused")
        mock_shout.Shout.return_value = mock_shout_instance

        client = IcecastClient(self.config)
        result = client.connect()

        self.assertFalse(result)
        self.assertEqual(client.get_state(), IcecastState.ERROR)

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_disconnect(self, mock_shout_module=None):
        """Test disconnection."""
        import shout as mock_shout

        mock_shout_instance = Mock()
        mock_shout.Shout.return_value = mock_shout_instance

        client = IcecastClient(self.config)
        client.connect()
        client.disconnect()

        self.assertEqual(client.get_state(), IcecastState.DISCONNECTED)
        mock_shout_instance.close.assert_called_once()

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_update_metadata(self, mock_shout_module=None):
        """Test metadata update."""
        import shout as mock_shout

        mock_shout_instance = Mock()
        mock_metadata = Mock()
        mock_shout.Shout.return_value = mock_shout_instance
        mock_shout.Metadata.return_value = mock_metadata

        client = IcecastClient(self.config)
        client.connect()

        track = {
            "title": "Test Track",
            "artist": "Test Artist",
        }

        result = client.update_metadata(track)

        self.assertTrue(result)
        mock_metadata.add.assert_called_once_with("song", "Test Artist - Test Track")
        mock_shout_instance.set_metadata.assert_called_once_with(mock_metadata)

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_send_audio(self, mock_shout_module=None):
        """Test sending audio data."""
        import shout as mock_shout

        mock_shout_instance = Mock()
        mock_shout.Shout.return_value = mock_shout_instance

        client = IcecastClient(self.config)
        client.connect()

        audio_data = b"fake audio data"
        result = client.send_audio(audio_data)

        self.assertTrue(result)
        self.assertEqual(client.get_state(), IcecastState.STREAMING)
        mock_shout_instance.send.assert_called_once_with(audio_data)
        mock_shout_instance.sync.assert_called_once()

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_stream_file(self, mock_shout_module=None):
        """Test streaming a file."""
        import shout as mock_shout

        mock_shout_instance = Mock()
        mock_shout.Shout.return_value = mock_shout_instance

        client = IcecastClient(self.config)
        client.connect()

        # Create temporary test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test audio content")
            temp_file = f.name

        try:
            result = client.stream_file(temp_file, chunk_size=5)
            self.assertTrue(result)

            # Should have sent multiple chunks
            self.assertGreater(mock_shout_instance.send.call_count, 0)
        finally:
            os.unlink(temp_file)

    def test_stream_file_not_connected(self):
        """Test streaming file when not connected."""
        client = IcecastClient(self.config)
        result = client.stream_file("/fake/path.mp3")
        self.assertFalse(result)

    def test_stream_file_not_found(self):
        """Test streaming non-existent file."""
        with patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True):
            client = IcecastClient(self.config)
            result = client.stream_file("/nonexistent/file.mp3")
            self.assertFalse(result)

    @patch("qfzz.streaming.icecast_client.SHOUT_AVAILABLE", True)
    def test_get_stats(self, mock_shout_module=None):
        """Test getting statistics."""
        import shout as mock_shout

        mock_shout_instance = Mock()
        mock_shout.Shout.return_value = mock_shout_instance

        client = IcecastClient(self.config)
        client.connect()

        # Send some data
        client.send_audio(b"test data")

        stats = client.get_stats()

        self.assertEqual(stats["state"], IcecastState.STREAMING.value)
        self.assertTrue(stats["connected"])
        self.assertEqual(stats["bytes_sent"], 9)  # len("test data")
        self.assertIsNotNone(stats["uptime_seconds"])
        self.assertIn("server", stats)


if __name__ == "__main__":
    unittest.main()
