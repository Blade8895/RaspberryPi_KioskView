#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

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

sudo apt install -y python3 python3-venv python3-pip "$CHROMIUM_PACKAGE"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p downloads/cache logs

echo "Installation abgeschlossen."
