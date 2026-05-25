#!/bin/sh
set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="start-session"
REPO="LaGrandma/Claude-Ping"
RAW_URL="https://raw.githubusercontent.com/${REPO}/main/start-session.py"

echo "Installing ${SCRIPT_NAME}..."

curl -fsSL "$RAW_URL" -o "${INSTALL_DIR}/${SCRIPT_NAME}"
chmod +x "${INSTALL_DIR}/${SCRIPT_NAME}"

echo "Done! Run: ${SCRIPT_NAME}"
