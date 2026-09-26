# Icecast Streaming Guide

This guide explains how to use QFZZ with Icecast for production-grade audio streaming.

## Overview

QFZZ now supports streaming to Icecast servers for:
- **Concurrent listeners**: Handle multiple simultaneous listeners
- **Better buffering**: Icecast handles client buffering
- **Industry standard**: Compatible with all Icecast-compatible players
- **Scalability**: Handles production workloads

## Architecture

```
QFZZ Application (Source Client)
         ↓
    Icecast Server
         ↓
    Multiple Listeners
```

The QFZZ application acts as a **source client** that sends audio to the Icecast server, which then distributes it to multiple listeners.

## Quick Start

### 1. Install Icecast

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install icecast2
```

**macOS:**
```bash
brew install icecast
```

**From source:**
Visit https://icecast.org/download/

### 2. Install Python Dependencies

For Icecast streaming, you need `python-shout` (binding to libshout):

**Ubuntu/Debian:**
```bash
# Install libshout development headers
sudo apt-get install libshout3-dev

# Install Python package
pip install python-shout
```

**macOS:**
```bash
# Install libshout
brew install libshout

# Install Python package
pip install python-shout
```

### 3. Start Icecast Server

QFZZ includes a pre-configured Icecast setup:

```bash
./scripts/start-icecast.sh
```

Or manually:
```bash
icecast2 -c config/icecast.xml
```

The server will start on **http://localhost:8000**

### 4. Use QFZZ with Icecast

#### Python API

```python
from qfzz.streaming import IcecastClient, IcecastConfig

# Configure connection
config = IcecastConfig(
    host="localhost",
    port=8000,
    password="hackme",  # Change in production!
    mount="/qfzz",
    name="QFZZ Radio",
    description="AI-powered radio",
    genre="Electronic",
    bitrate=128,
)

# Create and connect client
client = IcecastClient(config)
if client.connect():
    # Update now playing info
    client.update_metadata({
        "title": "Quantum Resonance",
        "artist": "QFZZ AI",
    })
    
    # Stream a file
    client.stream_file("/path/to/audio.mp3")
    
    # Get statistics
    stats = client.get_stats()
    print(f"Streamed {stats['bytes_sent']:,} bytes")
    
    # Disconnect
    client.disconnect()
```

#### Demo Script

Run the included demo:

```bash
python examples/icecast_streaming_demo.py
```

## Configuration

### Icecast Server Config

The main config file is `config/icecast.xml`. Key settings:

```xml
<listen-socket>
    <port>8000</port>
</listen-socket>

<authentication>
    <source-password>hackme</source-password>
    <admin-password>hackme</admin-password>
</authentication>

<mount type="normal">
    <mount-name>/qfzz</mount-name>
    <max-listeners>100</max-listeners>
</mount>
```

**Important**: Change passwords in production!

### Python Client Config

Use `IcecastConfig` dataclass:

```python
config = IcecastConfig(
    # Connection
    host="localhost",
    port=8000,
    password="hackme",
    mount="/qfzz",
    protocol="http",  # or "https"
    
    # Stream metadata
    name="Your Stream Name",
    description="Your description",
    genre="Your genre",
    url="https://your-website.com",
    
    # Audio format
    format="mp3",  # or "ogg"
    bitrate=128,   # kbps
    samplerate=44100,  # Hz
    channels=2,    # stereo
    
    # Connection settings
    reconnect_attempts=3,
    reconnect_delay=5.0,
    
    # Visibility
    public=False,  # True to list in directory
)
```

## Usage Patterns

### Continuous Streaming

For 24/7 streaming, use the background thread:

```python
from qfzz.streaming import IcecastClient, IcecastConfig

config = IcecastConfig(host="localhost", port=8000, password="hackme", mount="/qfzz")
client = IcecastClient(config)

# Connect
client.connect()

# Define playlist callback
def get_next_track():
    # Your logic to get next track
    return {
        "title": "Song Title",
        "artist": "Artist Name",
        "filepath": "/path/to/song.mp3",
    }

# Start streaming thread
client.start_streaming_thread(get_next_track)

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.stop_streaming_thread()
    client.disconnect()
```

### Manual Control

For manual track-by-track control:

```python
client = IcecastClient(config)
client.connect()

for track in playlist:
    client.update_metadata(track)
    client.stream_file(track["filepath"])

client.disconnect()
```

### Monitoring

Get real-time statistics:

```python
stats = client.get_stats()
print(f"State: {stats['state']}")
print(f"Connected: {stats['connected']}")
print(f"Bytes sent: {stats['bytes_sent']:,}")
print(f"Uptime: {stats['uptime_seconds']:.1f}s")
print(f"Current track: {stats['current_track']}")
```

## Listening to the Stream

Once streaming, listeners can connect using:

### Direct URL
```
http://localhost:8000/qfzz
```

### With Media Players

**VLC:**
```bash
vlc http://localhost:8000/qfzz
```

**mpv:**
```bash
mpv http://localhost:8000/qfzz
```

**Browser:**
Just open the URL in your browser

### Web Interface

Icecast provides a web interface:
- **Status**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/ (username: admin, password: hackme)

## Production Deployment

### Security

1. **Change all passwords** in `config/icecast.xml`
2. **Use HTTPS** if streaming over internet
3. **Firewall**: Only expose port 8000 if needed
4. **Limit connections**: Set appropriate `<max-listeners>`

### Performance

1. **Choose appropriate bitrate**:
   - 64 kbps: Low quality, low bandwidth
   - 128 kbps: Good quality (default)
   - 192 kbps: High quality
   - 320 kbps: Maximum quality

2. **Monitor resources**:
   ```bash
   # Check Icecast status
   curl http://localhost:8000/status.xsl
   ```

3. **Log rotation**: Configure in `<logging>` section

### Reliability

1. **Auto-restart**: Use systemd or supervisor to keep Icecast running
2. **Reconnection**: The client automatically handles reconnection
3. **Error handling**: Monitor logs for issues

### Example systemd Service

Create `/etc/systemd/system/qfzz-icecast.service`:

```ini
[Unit]
Description=QFZZ Icecast Server
After=network.target

[Service]
Type=simple
User=qfzz
WorkingDirectory=/opt/qfzz
ExecStart=/usr/bin/icecast2 -c /opt/qfzz/config/icecast.xml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable qfzz-icecast
sudo systemctl start qfzz-icecast
sudo systemctl status qfzz-icecast
```

## Troubleshooting

### Connection refused

**Problem**: Cannot connect to Icecast server

**Solutions**:
- Check Icecast is running: `ps aux | grep icecast`
- Check port is open: `netstat -tlnp | grep 8000`
- Verify config: `icecast2 -c config/icecast.xml`

### Wrong password

**Problem**: Authentication failed

**Solutions**:
- Check `source-password` in `config/icecast.xml`
- Ensure password matches in your Python code
- Restart Icecast after config changes

### No audio

**Problem**: Connected but no sound

**Solutions**:
- Check audio file format is supported (MP3, OGG)
- Verify file exists and is readable
- Check Icecast logs: `/var/log/icecast2/error.log`
- Test with `examples/icecast_streaming_demo.py`

### High latency

**Problem**: Significant delay between source and listeners

**Solutions**:
- Reduce `<burst-size>` in config
- Increase bitrate
- Check network bandwidth
- Use local network for testing

### python-shout not available

**Problem**: Import error for shout module

**Solutions**:
```bash
# Install libshout development files
sudo apt-get install libshout3-dev

# Install Python binding
pip install python-shout

# Or use conda
conda install -c conda-forge python-shout
```

## API Reference

### IcecastClient

Main class for streaming to Icecast.

**Methods**:
- `connect() -> bool`: Connect to server
- `disconnect() -> None`: Disconnect from server
- `update_metadata(track: dict) -> bool`: Update now playing info
- `send_audio(data: bytes) -> bool`: Send raw audio data
- `stream_file(filepath: str) -> bool`: Stream an audio file
- `start_streaming_thread(callback) -> bool`: Start background streaming
- `stop_streaming_thread() -> None`: Stop background streaming
- `get_state() -> IcecastState`: Get current state
- `get_stats() -> dict`: Get streaming statistics

### IcecastConfig

Configuration dataclass.

**Fields**:
- `host: str`: Server hostname
- `port: int`: Server port
- `password: str`: Source password
- `mount: str`: Mount point (e.g., "/qfzz")
- `name: str`: Stream name
- `description: str`: Stream description
- `genre: str`: Stream genre
- `url: str`: Stream website
- `format: str`: Audio format ("mp3" or "ogg")
- `bitrate: int`: Bitrate in kbps
- `samplerate: int`: Sample rate in Hz
- `channels: int`: Number of channels (1=mono, 2=stereo)
- `public: bool`: List in directory

### IcecastState

Enum of client states:
- `DISCONNECTED`: Not connected
- `CONNECTED`: Connected but not streaming
- `STREAMING`: Actively streaming
- `ERROR`: Error state

## Integration with QFZZ

To use Icecast with the main QFZZ application:

```python
from qfzz import QFZZStation, StationConfig
from qfzz.streaming import IcecastClient, IcecastConfig, MusicPlayer

# Start Icecast client
icecast_config = IcecastConfig(
    host="localhost",
    port=8000,
    password="hackme",
    mount="/qfzz"
)
icecast = IcecastClient(icecast_config)
icecast.connect()

# Start QFZZ station
station_config = StationConfig(
    station_id="icecast_001",  # required on live tip
    station_name="QFZZ Prime",
    enable_blockchain=True
)
station = QFZZStation(station_config)
station.start()

# Connect player to Icecast
player = MusicPlayer()
# ... integrate player with icecast client ...
```

## Resources

- **Icecast Documentation**: https://icecast.org/docs/
- **libshout Documentation**: https://www.icecast.org/docs/libshout/
- **python-shout**: https://pypi.org/project/python-shout/
- **QFZZ Repository**: https://github.com/fuzzywigg/QFZZ

## Support

For issues with:
- **Icecast server**: Visit https://icecast.org/
- **QFZZ integration**: Open an issue on GitHub
- **python-shout**: Check PyPI documentation

---

**Note**: Icecast streaming is optional. QFZZ works without it using the built-in HTTP server for local/development use.
