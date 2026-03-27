#!/usr/bin/env bash
set -euo pipefail
sleep 5

CHROMIUM_BIN="$(command -v chromium || true)"
if [[ -z "$CHROMIUM_BIN" ]]; then
  CHROMIUM_BIN="$(command -v chromium-browser || true)"
fi

if [[ -z "$CHROMIUM_BIN" ]]; then
  echo "Fehler: Chromium wurde nicht gefunden (weder 'chromium-browser' noch 'chromium')."
  exit 1
fi

"$CHROMIUM_BIN" --noerrdialogs --disable-infobars --kiosk --incognito --check-for-update-interval=31536000 http://localhost:5000/
