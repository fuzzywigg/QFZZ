# Streaming API

The streaming module provides local HTTP audio streaming with playlist APIs,
buffer/prefetch session metadata, and reconnect support.

## MusicPlayer

::: qfzz.streaming.player.MusicPlayer
    options:
      show_root_heading: true
      show_source: true

## Implemented Endpoints

- `GET /playlist.json`
  - Returns current queue with streamable URLs.
- `GET /stream/session.json`
  - Returns active stream state, current track, prefetch tracks, buffer settings, reconnect counters, and last error.
- `GET /stream/manifest.m3u8`
  - Returns an HLS-compatible playlist manifest generated from the loaded queue.
- `POST /stream/reconnect`
  - Triggers server-side reconnect/recovery logic and returns `{ "recovered": true|false }`.
- `GET /ledger.json`, `GET /dj_message.json`, `GET /graph.json`
  - Ancillary metadata APIs for UI integration.

Audio files are served with `Accept-Ranges` and short-lived cache headers for playback buffering on slow/noisy networks.

## Usage Example

```python
from qfzz import MusicPlayer
from qfzz.datasets import DatasetManager

# Create player
manager = DatasetManager()
player = MusicPlayer(dataset_manager=manager)

# Load from dataset-backed library
player.load_playlist_from_datasets()
player.play()

# Inspect streaming session metadata
session = player.get_stream_status()
print(session["buffer_seconds"], session["prefetch_tracks"])
```
