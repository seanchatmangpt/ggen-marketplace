#!/usr/bin/env bash
set -euo pipefail

DEST_DIR="$(pwd)/bin"
mkdir -p "$DEST_DIR"

echo "=== Downloading official AAIF Binaries into $DEST_DIR ==="

# 1. agentgateway & agctl
if [ ! -f "$DEST_DIR/agentgateway" ]; then
    echo "Downloading agentgateway v1.6.0..."
    curl -sSL "https://github.com/agentgateway/agentgateway/releases/download/v1.6.0/agentgateway-darwin-arm64" -o "$DEST_DIR/agentgateway"
    chmod +x "$DEST_DIR/agentgateway"
fi

if [ ! -f "$DEST_DIR/agctl" ]; then
    echo "Downloading agctl v1.6.0..."
    curl -sSL "https://github.com/agentgateway/agentgateway/releases/download/v1.6.0/agctl-darwin-arm64" -o "$DEST_DIR/agctl"
    chmod +x "$DEST_DIR/agctl"
fi

# 2. agent-router (aigw)
if [ ! -f "$DEST_DIR/aigw" ]; then
    echo "Downloading agent-router aigw v1.1.0..."
    curl -sSL "https://github.com/theagentrouter/agent-router/releases/download/v1.1.0/aigw-darwin-arm64" -o "$DEST_DIR/aigw"
    chmod +x "$DEST_DIR/aigw"
fi

# 3. goose
if [ ! -f "$DEST_DIR/goose" ]; then
    echo "Downloading aaif-goose v1.53.0..."
    curl -sSL "https://github.com/aaif-goose/goose/releases/download/v1.53.0/goose-aarch64-apple-darwin.tar.gz" -o "/tmp/goose.tar.gz"
    tar -xzf "/tmp/goose.tar.gz" -C "$DEST_DIR"
    rm -f "/tmp/goose.tar.gz"
    chmod +x "$DEST_DIR/goose"
fi

echo "=== Verifying downloaded AAIF binaries ==="
"$DEST_DIR/agentgateway" --help | head -n 3 || true
"$DEST_DIR/agctl" --help | head -n 3 || true
"$DEST_DIR/aigw" --help | head -n 3 || true
"$DEST_DIR/goose" --version || true
echo "=== AAIF Binaries successfully installed in $DEST_DIR ==="
