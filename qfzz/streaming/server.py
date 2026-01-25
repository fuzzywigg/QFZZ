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
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
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
            
            handler = partial(AudioRequestHandler, directory=self.content_dir)
            
            self.httpd = socketserver.TCPServer(("", self.port), handler)
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
