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
# Resolve default SRC_DIR from the invoking user's home, not root's
# (sudo resets $HOME to /root unless -E is passed with HOME preserved).
if [[ -z "${SRC_DIR:-}" ]]; then
    if [[ -n "${SUDO_USER:-}" ]]; then
        SRC_DIR="$(getent passwd "$SUDO_USER" | cut -d: -f6)/SageDocs"
    else
        SRC_DIR="$HOME/SageDocs"
    fi
fi
DEPLOY_DIR="/var/www/sagedocs"
BACKUP_DIR="/var/www/backups/sagedocs"
MAX_BACKUPS=5
SERVICE_USER="www-data"
SERVICE_GROUP="www-data"
SERVICE_NAME="sagedocs"

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

echo "=== SageDocs Deploy ==="
echo "Source:  $SRC_DIR"
echo "Target:  $DEPLOY_DIR"
echo ""

# --- Step 1: Pull latest code in source repo ---
# Run git pull as the owner of SRC_DIR so SSH keys / git config resolve correctly.
# Skip entirely when SKIP_GIT_PULL=1 (e.g. CI has already checked out the code).
echo "[1/7] Pulling latest code in $SRC_DIR..."
cd "$SRC_DIR"
if [[ "${SKIP_GIT_PULL:-0}" == "1" ]]; then
    echo "  Skipping git pull (SKIP_GIT_PULL=1)."
else
    SRC_OWNER=$(stat -c '%U' "$SRC_DIR")
    sudo -u "$SRC_OWNER" git pull || echo "Warning: git pull failed (may not have remote configured)"
fi

# --- Step 2: Back up current deployment ---
if [[ -d "$DEPLOY_DIR/backend" ]]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"
    echo "[2/7] Backing up current deployment to $BACKUP_PATH..."
    mkdir -p "$BACKUP_DIR"

    rsync -a \
        --exclude 'venv/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        "$DEPLOY_DIR/" "$BACKUP_PATH/"

    echo "  Backup saved."

    # Prune old backups, keep only the most recent $MAX_BACKUPS
    BACKUP_COUNT=$(ls -1d "$BACKUP_DIR"/[0-9]* 2>/dev/null | wc -l)
    if [[ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]]; then
        REMOVE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
        echo "  Pruning $REMOVE_COUNT old backup(s)..."
        ls -1d "$BACKUP_DIR"/[0-9]* | head -n "$REMOVE_COUNT" | xargs rm -rf
    fi
else
    echo "[2/7] No existing deployment to back up (first deploy)."
fi

# --- Step 3: Create deploy dir and sync code ---
echo "[3/7] Syncing code to $DEPLOY_DIR..."
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

# --- Step 4: Set up venv and install dependencies (skip on --update) ---
if [[ "$UPDATE_ONLY" == false ]]; then
    echo "[4/7] Setting up Python virtual environment..."
    if [[ ! -d "$DEPLOY_DIR/venv" ]]; then
        python3 -m venv "$DEPLOY_DIR/venv"
        echo "  Created new venv."
    fi
else
    echo "[4/7] Skipping venv setup (--update mode)."
fi

echo "  Installing/updating dependencies..."
"$DEPLOY_DIR/venv/bin/pip" install --quiet --upgrade pip
"$DEPLOY_DIR/venv/bin/pip" install --quiet -r "$DEPLOY_DIR/backend/requirements.txt"

# --- Step 5: Create data directories (skip on --update) ---
if [[ "$UPDATE_ONLY" == false ]]; then
    echo "[5/7] Creating data directories..."
    mkdir -p "$DEPLOY_DIR/backend/data/chroma" \
             "$DEPLOY_DIR/backend/data/images" \
             "$DEPLOY_DIR/backend/data/analytics" \
             "$DEPLOY_DIR/backend/data/tenants" \
             "$DEPLOY_DIR/backend/uploads"
    echo "  Data directories ready."
else
    echo "[5/7] Skipping directory setup (--update mode)."
fi

# --- Step 6: Fix ownership ---
echo "[6/7] Setting ownership to $SERVICE_USER:$SERVICE_GROUP..."
chown -R "$SERVICE_USER":"$SERVICE_GROUP" "$DEPLOY_DIR"

# --- Step 7: Restart service ---
echo "[7/7] Restarting $SERVICE_NAME service..."
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
