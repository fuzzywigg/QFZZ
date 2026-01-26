#!/usr/bin/env bash
# Continuous ledger verification monitor for QFZZ

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LEDGER_FILE="$PROJECT_ROOT/qfzz_ledger.json"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # seconds
LOG_FILE="$PROJECT_ROOT/logs/ledger-verification.log"

mkdir -p "$PROJECT_ROOT/logs"

echo "========================================"
echo "QFZZ Ledger Continuous Verification"
echo "========================================"
echo ""
echo "Ledger: $LEDGER_FILE"
echo "Check interval: ${CHECK_INTERVAL}s"
echo "Log file: $LOG_FILE"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Counter for checks
CHECK_COUNT=0
FAIL_COUNT=0

while true; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    
    echo "[$TIMESTAMP] Check #$CHECK_COUNT..."
    
    # Run verification
    if python3 "$SCRIPT_DIR/verify-ledger.py" "$LEDGER_FILE" --quiet 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✓ VALID"
    else
        echo "  ✗ INVALID - Check log for details!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        
        # Send alert (customize as needed)
        echo "[$TIMESTAMP] ALERT: Ledger verification failed!" >> "$LOG_FILE"
        
        # Optional: Send email, Slack notification, etc.
        # mail -s "QFZZ Ledger Alert" admin@example.com < "$LOG_FILE"
    fi
    
    echo "  Total checks: $CHECK_COUNT, Failures: $FAIL_COUNT"
    echo ""
    
    # Wait before next check
    sleep "$CHECK_INTERVAL"
done
