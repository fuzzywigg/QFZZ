"""
Simple streaming server for QFZZ.
"""

import http.server
import socketserver
import threading
import logging
import os
import contextlib

logger = logging.getLogger(__name__)

import json

class AudioRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for audio streaming with CORS."""
    
    # Static playlist for now - will be dynamic later
    # This needs access to the player instance, but we are inside the handler
    # For now, we'll hardcode or use a class variable
    PAYLOAD = []
    GRAPH_PAYLOAD = {}
    DJ_MESSAGE = {"message": "Welcome to QFZZ, the Pulse of the Quantum Realm."}
    LEDGER_STATS = {"height": 0, "status": "Waiting"}

    def do_POST(self):
        """Handle content requests."""
        if self.path == '/request':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                url = data.get('url')
                if url and hasattr(AudioRequestHandler, 'DJ_INSTANCE'):
                    # Async or Sync? For demo, sync.
                    # We need a reference to the DJ instance in the handler.
                    # This is tricky with SimpleHTTPRequestHandler.
                    # Solution: We assign it as a static property on startup.
                    
                    track = AudioRequestHandler.DJ_INSTANCE.request_track(url)
                    if track:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "queued", "track": track}).encode('utf-8'))
                        
                        # Add to playlist? We need a reference to Player too.
                        if hasattr(AudioRequestHandler, 'PLAYER_INSTANCE'):
                             AudioRequestHandler.PLAYER_INSTANCE.add_track(track)
                        return
                        
            except Exception as e:
                logger.error(f"Request failed: {e}")
                
            self.send_response(400)
            self.end_headers()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/playlist.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(AudioRequestHandler.PAYLOAD)
            self.wfile.write(response.encode('utf-8'))
            
        elif self.path == '/graph.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(AudioRequestHandler.GRAPH_PAYLOAD)
            self.wfile.write(response.encode('utf-8'))
            
        elif self.path == '/dj_message.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(AudioRequestHandler.DJ_MESSAGE)
            self.wfile.write(response.encode('utf-8'))
            
        elif self.path == '/ledger.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(AudioRequestHandler.LEDGER_STATS)
            self.wfile.write(response.encode('utf-8'))
            
        else:
            # Fallback to serving files
            super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        if self.command == 'OPTIONS':
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
            from functools import partial
            
            # Subclass to bind method to specific directory AND static instances
            # We need to capture content_dir from the outer instance
            cd = self.content_dir
            class Handler(AudioRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=cd, **kwargs)
            
            # Bind instances
            Handler.DJ_INSTANCE = self.dj if hasattr(self, 'dj') else None
            Handler.PLAYER_INSTANCE = self.player if hasattr(self, 'player') else None
            
            self.httpd = socketserver.TCPServer(("", self.port), Handler)
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
