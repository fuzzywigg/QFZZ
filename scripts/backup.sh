#!/usr/bin/env bash
# QFZZ Automated Backup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

echo "========================================"
echo "QFZZ Backup Script"
echo "========================================"
echo ""
echo "Project: $PROJECT_ROOT"
echo "Backup destination: $BACKUP_PATH"
echo "Retention: $RETENTION_DAYS days"
echo ""

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup critical files
echo "Backing up critical files..."

# Ledger
if [ -f "$PROJECT_ROOT/qfzz_ledger.json" ]; then
    cp "$PROJECT_ROOT/qfzz_ledger.json" "$BACKUP_PATH/"
    echo "  ✓ Ledger backed up"
else
    echo "  ⚠ Ledger not found"
fi

# Knowledge graph
if [ -f "$PROJECT_ROOT/qfzz_knowledge_graph.json" ]; then
    cp "$PROJECT_ROOT/qfzz_knowledge_graph.json" "$BACKUP_PATH/"
    echo "  ✓ Knowledge graph backed up"
else
    echo "  ⚠ Knowledge graph not found"
fi

# Honeycomb state
if [ -d "$PROJECT_ROOT/honeycomb" ]; then
    cp -r "$PROJECT_ROOT/honeycomb" "$BACKUP_PATH/"
    echo "  ✓ Honeycomb state backed up"
else
    echo "  ⚠ Honeycomb directory not found"
fi

# Configuration
if [ -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env" "$BACKUP_PATH/"
    echo "  ✓ Environment config backed up"
fi

if [ -d "$PROJECT_ROOT/config" ]; then
    cp -r "$PROJECT_ROOT/config" "$BACKUP_PATH/"
    echo "  ✓ Configuration backed up"
fi

# Audio content (optional - can be large)
if [ "${BACKUP_AUDIO:-false}" = "true" ]; then
    if [ -d "$PROJECT_ROOT/qfzz_audio_content" ]; then
        echo "  ⟳ Backing up audio content (this may take a while)..."
        cp -r "$PROJECT_ROOT/qfzz_audio_content" "$BACKUP_PATH/"
        echo "  ✓ Audio content backed up"
    fi
fi

# Create tarball
echo ""
echo "Creating compressed archive..."
cd "$BACKUP_DIR"
tar czf "${TIMESTAMP}.tar.gz" "$TIMESTAMP"
rm -rf "$TIMESTAMP"
echo "  ✓ Archive created: ${TIMESTAMP}.tar.gz"

# Calculate size
SIZE=$(du -h "${TIMESTAMP}.tar.gz" | cut -f1)
echo "  Size: $SIZE"

# Verify backup
echo ""
echo "Verifying backup..."
if tar tzf "${TIMESTAMP}.tar.gz" > /dev/null 2>&1; then
    echo "  ✓ Backup verified"
else
    echo "  ✗ Backup verification failed!"
    exit 1
fi

# Clean old backups
echo ""
echo "Cleaning old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "  ✓ Old backups cleaned"

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -5 || echo "  No backups found"

echo ""
echo "========================================"
echo "Backup complete!"
echo "========================================"
echo ""
echo "Backup location: $BACKUP_DIR/${TIMESTAMP}.tar.gz"
echo ""

# Create metadata
cat > "$BACKUP_DIR/${TIMESTAMP}.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$(date -Iseconds)",
  "size": "$SIZE",
  "files": [
    "qfzz_ledger.json",
    "qfzz_knowledge_graph.json",
    "honeycomb/",
    ".env",
    "config/"
  ]
}
EOF

exit 0
