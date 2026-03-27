#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

sudo apt update
sudo apt install -y python3 python3-venv python3-pip chromium-browser

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p downloads/cache logs

echo "Installation abgeschlossen."
