#!/usr/bin/env bash
# QFZZ Restore Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"

# Check argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | xargs -n1 basename | sed 's/.tar.gz$//'
    exit 1
fi

TIMESTAMP=$1
BACKUP_FILE="$BACKUP_DIR/${TIMESTAMP}.tar.gz"

echo "========================================"
echo "QFZZ Restore Script"
echo "========================================"
echo ""

# Verify backup exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup not found: $BACKUP_FILE"
    exit 1
fi

echo "Backup file: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"
echo ""

# Confirm
read -p "This will overwrite current data. Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Extracting to $TEMP_DIR..."

# Extract
tar xzf "$BACKUP_FILE" -C "$TEMP_DIR"
EXTRACTED_DIR="$TEMP_DIR/$TIMESTAMP"

# Restore files
echo ""
echo "Restoring files..."

for file in qfzz_ledger.json qfzz_knowledge_graph.json .env; do
    if [ -f "$EXTRACTED_DIR/$file" ]; then
        cp "$EXTRACTED_DIR/$file" "$PROJECT_ROOT/"
        echo "  ✓ Restored $file"
    fi
done

for dir in honeycomb config; do
    if [ -d "$EXTRACTED_DIR/$dir" ]; then
        cp -r "$EXTRACTED_DIR/$dir" "$PROJECT_ROOT/"
        echo "  ✓ Restored $dir/"
    fi
done

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "Restore complete!"
echo "========================================"
echo ""
echo "Verification recommended:"
echo "  python scripts/verify-ledger.py"
echo ""

exit 0
