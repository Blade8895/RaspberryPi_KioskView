# RaspberryPi KioskView

Flask-basierte TV-Anzeige für XLSX-Dateien aus einem öffentlichen Nextcloud-Ordnerlink.

## Schnellstart auf dem Pi

```bash
chmod +x setup.sh
./setup.sh <REPO_URL>
cd ~/RaspberryPi_KioskView
./run.sh
```

Optional kannst du beim Setup auch einen Branch auswählen:

```bash
./setup.sh <REPO_URL> ~/RaspberryPi_KioskView <BRANCH>
```

- Anzeige: `http://<PI-IP>:5000/`
- Setup: `http://<PI-IP>:5000/plansetup`

## Autostart mit systemd

```bash
sudo cp deploy/kioskview.service /etc/systemd/system/kioskview.service
sudo systemctl daemon-reload
sudo systemctl enable kioskview.service
sudo systemctl start kioskview.service
```

## Kiosk-Modus (Chromium)

```bash
./kiosk-start.sh
```

Hinweis: Die Setup-Skripte erkennen automatisch, ob auf deinem System das Paket
`chromium-browser` oder `chromium` verfügbar ist.

Für LXDE-Autostart:

`~/.config/lxsession/LXDE-pi/autostart`

```txt
@/home/pi/RaspberryPi_KioskView/kiosk-start.sh
```
