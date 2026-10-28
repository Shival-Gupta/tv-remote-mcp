#!/usr/bin/env bash
# TV Remote MCP — Unix/macOS One-Click Installer
set -e

# Detect Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "[ERR] Python 3 is required but was not found on PATH."
    exit 1
fi

echo "=================================================================="
echo "  TV Remote MCP — Installer Wrapper"
echo "=================================================================="
exec $PYTHON_CMD "$(dirname "$0")/install.py" "$@"
