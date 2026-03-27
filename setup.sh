#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-}"
TARGET_DIR="${2:-$HOME/RaspberryPi_KioskView}"

if [[ -z "$REPO_URL" ]]; then
  echo "Nutzung: ./setup.sh <git_repo_url> [zielverzeichnis]"
  echo "Beispiel: ./setup.sh https://github.com/USER/RaspberryPi_KioskView.git"
  exit 1
fi

sudo apt update
sudo apt install -y git python3 python3-venv python3-pip chromium-browser

if [[ -d "$TARGET_DIR/.git" ]]; then
  echo "Repository bereits vorhanden -> git pull"
  git -C "$TARGET_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

chmod +x run.sh kiosk-start.sh install.sh || true
mkdir -p downloads/cache logs

echo "Setup abgeschlossen."
echo "Start: cd $TARGET_DIR && ./run.sh"
