"""
Simple streaming server for QFZZ.
"""

import http.server
import json
import logging
import socketserver
import threading
from base64 import b64encode
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class AudioRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for audio streaming with CORS."""

    # Static playlist for now - will be dynamic later
    # This needs access to the player instance, but we are inside the handler
    # For now, we'll hardcode or use a class variable
    PAYLOAD = []
    GRAPH_PAYLOAD = {}
    DJ_MESSAGE = {"message": "Welcome to QFZZ, the Pulse of the Quantum Realm."}
    LEDGER_STATS = {"height": 0, "status": "Waiting"}
    STREAM_STATUS = {
        "state": "stopped",
        "current_track": None,
        "prefetch_tracks": [],
        "buffer_seconds": 8,
        "reconnect": {"attempts": 0, "max_attempts": 3},
        "error": None,
    }
    STREAM_STATUS_PROVIDER = None
    STREAM_MANIFEST_PROVIDER = None
    STREAM_ERROR_HANDLER = None

    def _read_json_body(self):
        """Read JSON body from request."""
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(body) if body else {}

    def _send_json(self, payload, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_POST(self):
        """Handle content requests."""
        parsed = urlparse(self.path)
        if parsed.path == "/request":
            try:
                data = self._read_json_body()
                url = data.get("url")
                if url and hasattr(AudioRequestHandler, "DJ_INSTANCE"):
                    # Async or Sync? For demo, sync.
                    # We need a reference to the DJ instance in the handler.
                    # This is tricky with SimpleHTTPRequestHandler.
                    # Solution: We assign it as a static property on startup.

                    track = AudioRequestHandler.DJ_INSTANCE.request_track(url)
                    if track:
                        self._send_json({"status": "queued", "track": track}, 200)

                        # Add to playlist? We need a reference to Player too.
                        if hasattr(AudioRequestHandler, "PLAYER_INSTANCE"):
                            AudioRequestHandler.PLAYER_INSTANCE.add_track(track)
                        return

            except Exception as e:
                logger.error(f"Request failed: {e}")

            self.send_response(400)
            self.end_headers()
        elif parsed.path == "/api/dj/chat":
            try:
                data = self._read_json_body()
                user_id = str(data.get("user_id", "anonymous"))
                message = str(data.get("message", "")).strip()
                include_tts = bool(data.get("include_tts", False))

                if not message:
                    self._send_json({"error": "message is required"}, 400)
                    return

                dj = getattr(AudioRequestHandler, "DJ_INSTANCE", None)
                if not dj or not hasattr(dj, "interact"):
                    self._send_json({"error": "DJ instance is not available"}, 503)
                    return

                response_text = dj.interact(user_id, message)
                payload = {"user_id": user_id, "response": response_text}

                if include_tts and getattr(dj, "ai_dj", None):
                    audio = dj.ai_dj.synthesize_speech(response_text)
                    if audio:
                        payload["tts_included"] = True
                        payload["tts_audio_base64"] = b64encode(audio).decode("ascii")
                        payload["tts_format"] = "mp3"
                    else:
                        payload["tts_included"] = False

                self._send_json(payload, 200)
            except Exception as e:
                logger.error(f"DJ chat request failed: {e}")
                self._send_json({"error": "Failed to process DJ chat request"}, 500)
        elif parsed.path == "/api/dj/recommendations":
            try:
                data = self._read_json_body()
                user_id = str(data.get("user_id", "anonymous"))
                message = str(data.get("message", ""))
                preferences = data.get("preferences")
                if preferences is not None and not isinstance(preferences, dict):
                    self._send_json({"error": "preferences must be an object"}, 400)
                    return

                max_tracks = int(data.get("max_tracks", 5))
                include_tts = bool(data.get("include_tts", False))

                dj = getattr(AudioRequestHandler, "DJ_INSTANCE", None)
                if not dj or not hasattr(dj, "generate_llm_recommendation_response"):
                    self._send_json(
                        {"error": "DJ recommendation integration is not available"},
                        503,
                    )
                    return

                payload = dj.generate_llm_recommendation_response(
                    user_id=user_id,
                    message=message,
                    preferences=preferences,
                    max_tracks=max_tracks,
                    include_tts=include_tts,
                )
                self._send_json(payload, 200)
            except Exception as e:
                logger.error(f"DJ recommendation request failed: {e}")
                self._send_json({"error": "Failed to process recommendation request"}, 500)
        elif parsed.path == "/stream/reconnect":
            if callable(AudioRequestHandler.STREAM_ERROR_HANDLER):
                recovered = AudioRequestHandler.STREAM_ERROR_HANDLER(
                    "client-reconnect-request", recoverable=True
                )
                self._send_json({"recovered": bool(recovered)}, 200 if recovered else 503)
            else:
                self.send_response(503)
                self.end_headers()
        else:
            self.send_error(404)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/playlist.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps(AudioRequestHandler.PAYLOAD)
            self.wfile.write(response.encode("utf-8"))

        elif path == "/graph.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps(AudioRequestHandler.GRAPH_PAYLOAD)
            self.wfile.write(response.encode("utf-8"))

        elif path == "/dj_message.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps(AudioRequestHandler.DJ_MESSAGE)
            self.wfile.write(response.encode("utf-8"))

        elif path == "/ledger.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps(AudioRequestHandler.LEDGER_STATS)
            self.wfile.write(response.encode("utf-8"))
        elif path == "/stream/session.json":
            if callable(AudioRequestHandler.STREAM_STATUS_PROVIDER):
                AudioRequestHandler.STREAM_STATUS = (
                    AudioRequestHandler.STREAM_STATUS_PROVIDER()
                    or AudioRequestHandler.STREAM_STATUS
                )
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps(AudioRequestHandler.STREAM_STATUS)
            self.wfile.write(response.encode("utf-8"))
        elif path == "/stream/manifest.m3u8":
            if callable(AudioRequestHandler.STREAM_MANIFEST_PROVIDER):
                manifest = AudioRequestHandler.STREAM_MANIFEST_PROVIDER()
            else:
                manifest = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-ENDLIST\n"
            self.send_response(200)
            self.send_header("Content-type", "application/vnd.apple.mpegurl")
            self.end_headers()
            self.wfile.write(manifest.encode("utf-8"))
        elif path == "/api/llm/providers":
            dj = getattr(AudioRequestHandler, "DJ_INSTANCE", None)
            if dj and getattr(dj, "llm_router", None) and hasattr(dj.llm_router, "get_status"):
                payload = dj.llm_router.get_status()
                self._send_json(payload, 200)
            else:
                self._send_json(
                    {
                        "total_providers": 0,
                        "available_providers": [],
                        "unavailable_providers": [],
                        "providers": [],
                    },
                    200,
                )

        else:
            # Fallback to serving files
            super().do_GET()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        parsed = urlparse(self.path)
        path = parsed.path.lower()
        audio_extensions = (".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a")
        if path.endswith(audio_extensions):
            self.send_header("Cache-Control", "public, max-age=300")
            self.send_header("Accept-Ranges", "bytes")
        else:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")

        if self.command == "OPTIONS":
            self.send_response(200)
            return super().end_headers()
        return super().end_headers()

    def log_message(self, format, *args):
        # Suppress default logging to keep console clean
        # pass # Enable for Debugging
        super().log_message(format, *args)


class StreamingServer:
    """
    Simple HTTP server to stream audio files.
    """

    def __init__(self, content_dir: str, port: int = 8000):
        self.content_dir = content_dir
        self.port = port
        self.httpd = None
        self.thread = None
        self.dj = None
        self.player = None

    def attach_instances(self, dj, player):
        """Attach DJ and Player instances."""
        self.dj = dj
        self.player = player
        # Fix: Update the RequestHandler class directly so running server sees them
        # (This works because Handler inherits/mixes in, or we just patch the base)
        AudioRequestHandler.DJ_INSTANCE = dj
        AudioRequestHandler.PLAYER_INSTANCE = player
        logger.info("Attached DJ and Player to Streaming Server")

    def set_playlist(self, playlist):
        """Update the playlist served by the API."""
        AudioRequestHandler.PAYLOAD = playlist

    def set_graph(self, graph_data):
        """Update the graph served by the API."""
        AudioRequestHandler.GRAPH_PAYLOAD = graph_data

    def set_dj_message(self, message: str):
        """Update the live DJ message."""
        AudioRequestHandler.DJ_MESSAGE = {"message": message}

    def set_ledger_stats(self, stats: dict):
        """Update the ledger stats."""
        AudioRequestHandler.LEDGER_STATS = stats

    def set_stream_status(self, status: dict):
        """Update stream status payload served by the API."""
        AudioRequestHandler.STREAM_STATUS = status

    def set_stream_status_provider(self, provider):
        """Attach callable provider for stream status."""
        AudioRequestHandler.STREAM_STATUS_PROVIDER = provider

    def set_stream_manifest_provider(self, provider):
        """Attach callable provider for HLS manifest content."""
        AudioRequestHandler.STREAM_MANIFEST_PROVIDER = provider

    def set_stream_error_handler(self, handler):
        """Attach callable recover handler for stream reconnect endpoint."""
        AudioRequestHandler.STREAM_ERROR_HANDLER = handler

    def start(self):
        """Start the streaming server in a background thread."""
        try:
            # Change to content dir so SimpleHTTPRequestHandler serves from there
            # But wait, changing global CWD is bad.
            # We should subclass SimpleHTTPRequestHandler to serve from specific dir
            # Or just tell python -m http.server to run there?
            # For a simple embedded server, let's just cheat and assume we configure
            # the path correctly or use a partial callback.

            # Better approach: partial with directory (available in Python 3.7+)

            # Subclass to bind method to specific directory AND static instances
            # We need to capture content_dir from the outer instance
            cd = self.content_dir

            class Handler(AudioRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=cd, **kwargs)

            # Bind instances
            Handler.DJ_INSTANCE = self.dj if hasattr(self, "dj") else None
            Handler.PLAYER_INSTANCE = self.player if hasattr(self, "player") else None

            self.httpd = socketserver.TCPServer(("", self.port), Handler)
            self.port = self.httpd.server_address[1]
            self.thread = threading.Thread(target=self.httpd.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            logger.info(f"Streaming server started at http://localhost:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming server: {e}")
            return False

    def stop(self):
        """Stop the streaming server."""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            logger.info("Streaming server stopped")
