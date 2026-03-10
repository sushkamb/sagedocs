#!/usr/bin/env bash
#
# deploy.sh — Sync code from git clone to deployment directory,
#              install/update dependencies, and restart the service.
#
# Usage:
#   sudo bash scripts/deploy.sh              # first-time setup + deploy
#   sudo bash scripts/deploy.sh --update     # code-only update (skip venv/dirs)
#

set -euo pipefail

# --- Configuration ---
SRC_DIR="/home/ubuntu/ForteAIBot"
DEPLOY_DIR="/var/www/forteaibot"
SERVICE_USER="www-data"
SERVICE_GROUP="www-data"
SERVICE_NAME="forteaibot"

# --- Parse flags ---
UPDATE_ONLY=false
if [[ "${1:-}" == "--update" ]]; then
    UPDATE_ONLY=true
fi

# --- Preflight checks ---
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

if [[ ! -d "$SRC_DIR" ]]; then
    echo "Error: Source directory $SRC_DIR does not exist."
    exit 1
fi

echo "=== ForteAI Deploy ==="
echo "Source:  $SRC_DIR"
echo "Target:  $DEPLOY_DIR"
echo ""

# --- Step 1: Pull latest code in source repo ---
echo "[1/6] Pulling latest code in $SRC_DIR..."
cd "$SRC_DIR"
sudo -u ubuntu git pull || echo "Warning: git pull failed (may not have remote configured)"

# --- Step 2: Create deploy dir and sync code ---
echo "[2/6] Syncing code to $DEPLOY_DIR..."
mkdir -p "$DEPLOY_DIR"

rsync -a --delete \
    --exclude '.env' \
    --exclude 'venv/' \
    --exclude 'data/' \
    --exclude 'uploads/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    "$SRC_DIR/" "$DEPLOY_DIR/"

echo "  Files synced."

# --- Step 3: Set up venv and install dependencies (skip on --update) ---
if [[ "$UPDATE_ONLY" == false ]]; then
    echo "[3/6] Setting up Python virtual environment..."
    if [[ ! -d "$DEPLOY_DIR/venv" ]]; then
        python3 -m venv "$DEPLOY_DIR/venv"
        echo "  Created new venv."
    fi
else
    echo "[3/6] Skipping venv setup (--update mode)."
fi

echo "  Installing/updating dependencies..."
"$DEPLOY_DIR/venv/bin/pip" install --quiet --upgrade pip
"$DEPLOY_DIR/venv/bin/pip" install --quiet -r "$DEPLOY_DIR/backend/requirements.txt"

# --- Step 4: Create data directories (skip on --update) ---
if [[ "$UPDATE_ONLY" == false ]]; then
    echo "[4/6] Creating data directories..."
    mkdir -p "$DEPLOY_DIR/backend/data/chroma" \
             "$DEPLOY_DIR/backend/data/images" \
             "$DEPLOY_DIR/backend/data/analytics" \
             "$DEPLOY_DIR/backend/data/tenants" \
             "$DEPLOY_DIR/backend/uploads"
    echo "  Data directories ready."
else
    echo "[4/6] Skipping directory setup (--update mode)."
fi

# --- Step 5: Fix ownership ---
echo "[5/6] Setting ownership to $SERVICE_USER:$SERVICE_GROUP..."
chown -R "$SERVICE_USER":"$SERVICE_GROUP" "$DEPLOY_DIR"

# --- Step 6: Restart service ---
echo "[6/6] Restarting $SERVICE_NAME service..."
if systemctl is-enabled "$SERVICE_NAME" &>/dev/null; then
    systemctl restart "$SERVICE_NAME"
    echo "  Service restarted."
else
    echo "  Warning: $SERVICE_NAME service not found. Set up systemd first (see docs/DEPLOYMENT.md)."
fi

echo ""
echo "=== Deploy complete ==="

# Quick health check
sleep 2
if curl -sf http://127.0.0.1:8100/health > /dev/null 2>&1; then
    echo "Health check: OK"
else
    echo "Health check: FAILED — check logs with: sudo journalctl -u $SERVICE_NAME -e"
fi
