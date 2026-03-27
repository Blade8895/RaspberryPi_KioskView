#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

sudo apt update

CHROMIUM_PACKAGE=""
if command -v chromium >/dev/null 2>&1; then
  echo "Chromium ist bereits installiert – Paketinstallation wird übersprungen."
elif apt-cache policy chromium 2>/dev/null | awk '/Candidate:/ {print $2}' | grep -qv '(none)'; then
  CHROMIUM_PACKAGE="chromium"
elif apt-cache policy chromium-browser 2>/dev/null | awk '/Candidate:/ {print $2}' | grep -qv '(none)'; then
  CHROMIUM_PACKAGE="chromium-browser"
else
  echo "Fehler: Chromium ist nicht installiert und kein installierbares Paket gefunden ('chromium' oder 'chromium-browser')."
  echo "Bitte Chromium manuell installieren und das Setup erneut ausführen."
  exit 1
fi

if [[ -n "$CHROMIUM_PACKAGE" ]]; then
  sudo apt install -y python3 python3-venv python3-pip "$CHROMIUM_PACKAGE"
else
  sudo apt install -y python3 python3-venv python3-pip
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p downloads/cache logs

echo "Installation abgeschlossen."
