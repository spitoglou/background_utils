#!/usr/bin/env bash
# Script to tail the background-utils log file
# Usage: ./scripts/tail_log.sh

set -euo pipefail

# Define the log file path (equivalent to $env:LOCALAPPDATA\background-utils\background-utils.log in PowerShell)
# On Linux/Mac, we'll use ~/.local/share/background-utils/background-utils.log as a similar location
LOG_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/background-utils/background-utils.log"

echo "Tailing background-utils.log (last 20 lines, live updates)"
echo "Press Ctrl+C to stop"
echo ""

if [[ -f "$LOG_FILE" ]]; then
    tail -n 20 -f "$LOG_FILE"
else
    echo "Error: Log file not found at $LOG_FILE"
    echo "Make sure the background-utils service is running and generating logs."
    exit 1
fi