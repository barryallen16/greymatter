#!/usr/bin/env bash
# One-command deploy: ./scripts/deploy.sh
# SSHs into the VPS, pulls, rebuilds in place, prunes stale images (free-tier disk is small).
set -euo pipefail
HOST="${VPS_HOST:-partha}"
DIR="${VPS_DIR:-~/greymatter}"
ssh "$HOST" "cd $DIR && git pull --ff-only && docker compose up -d --build --wait && docker image prune -f && docker compose ps"
