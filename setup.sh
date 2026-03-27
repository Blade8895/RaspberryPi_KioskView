#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-}"
TARGET_DIR="${2:-$HOME/RaspberryPi_KioskView}"
BRANCH="${3:-}"

if [[ -z "$REPO_URL" ]]; then
  echo "Nutzung: ./setup.sh <git_repo_url> [zielverzeichnis] [branch]"
  echo "Beispiel: ./setup.sh https://github.com/USER/RaspberryPi_KioskView.git ~/RaspberryPi_KioskView main"
  exit 1
fi

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
  sudo apt install -y git python3 python3-venv python3-pip "$CHROMIUM_PACKAGE"
else
  sudo apt install -y git python3 python3-venv python3-pip
fi

if [[ -d "$TARGET_DIR/.git" ]]; then
  echo "Repository bereits vorhanden"
  if [[ -n "$BRANCH" ]]; then
    echo "Wechsle auf Branch '$BRANCH' und aktualisiere"
    git -C "$TARGET_DIR" fetch --prune origin "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

    if ! git -C "$TARGET_DIR" show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
      echo "Fehler: Remote-Branch '$BRANCH' wurde auf 'origin' nicht gefunden."
      exit 1
    fi

    if git -C "$TARGET_DIR" show-ref --verify --quiet "refs/heads/$BRANCH"; then
      git -C "$TARGET_DIR" checkout "$BRANCH"
      git -C "$TARGET_DIR" branch --set-upstream-to="origin/$BRANCH" "$BRANCH" >/dev/null 2>&1 || true
    else
      git -C "$TARGET_DIR" checkout -b "$BRANCH" --track "origin/$BRANCH"
    fi
    git -C "$TARGET_DIR" pull --ff-only origin "$BRANCH"
  else
    echo "Aktualisiere aktuellen Branch"
    git -C "$TARGET_DIR" pull --ff-only
  fi
else
  if [[ -n "$BRANCH" ]]; then
    echo "Klonen von Branch '$BRANCH'"
    git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$TARGET_DIR"
  else
    git clone "$REPO_URL" "$TARGET_DIR"
  fi
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
