#!/bin/sh
set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="start-session"
REPO="LaGrandma/Claude-Ping"
RAW_URL="https://raw.githubusercontent.com/${REPO}/main/start-session.py"

echo "Installing ${SCRIPT_NAME}..."

curl -fsSL "$RAW_URL" -o "/tmp/${SCRIPT_NAME}"
chmod +x "/tmp/${SCRIPT_NAME}"
sudo mv "/tmp/${SCRIPT_NAME}" "${INSTALL_DIR}/${SCRIPT_NAME}"

echo "Done! Run: ${SCRIPT_NAME}"
