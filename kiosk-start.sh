#!/usr/bin/env bash
set -euo pipefail
sleep 5
chromium-browser --noerrdialogs --disable-infobars --kiosk --incognito --check-for-update-interval=31536000 http://localhost:5000/
