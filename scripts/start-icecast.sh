#!/usr/bin/env bash
# Start Icecast server for QFZZ

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/icecast.xml"

echo "========================================"
echo "QFZZ Icecast Server Startup"
echo "========================================"

# Check if Icecast is installed
if ! command -v icecast2 &> /dev/null; then
    echo "ERROR: Icecast2 not installed"
    echo ""
    echo "Install on Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install icecast2"
    echo ""
    echo "Install on macOS:"
    echo "  brew install icecast"
    echo ""
    echo "Install on other systems:"
    echo "  https://icecast.org/download/"
    exit 1
fi

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "Config: $CONFIG_FILE"
echo "Starting Icecast server..."
echo ""

# Start Icecast
icecast2 -c "$CONFIG_FILE"
