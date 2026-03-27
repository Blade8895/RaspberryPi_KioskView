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

CHROMIUM_PACKAGE=""
if apt-cache show chromium-browser >/dev/null 2>&1; then
  CHROMIUM_PACKAGE="chromium-browser"
elif apt-cache show chromium >/dev/null 2>&1; then
  CHROMIUM_PACKAGE="chromium"
else
  echo "Fehler: Weder 'chromium-browser' noch 'chromium' ist als apt-Paket verfügbar."
  echo "Bitte Chromium manuell installieren und das Setup erneut ausführen."
  exit 1
fi

sudo apt install -y git python3 python3-venv python3-pip "$CHROMIUM_PACKAGE"

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
