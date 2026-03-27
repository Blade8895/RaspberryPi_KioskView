import os
import threading
import time
from datetime import datetime


class UpdaterService:
    def __init__(self, settings_service, nextcloud_service, workbook_service, cache_dir, logger):
        self.settings_service = settings_service
        self.nextcloud_service = nextcloud_service
        self.workbook_service = workbook_service
        self.cache_dir = cache_dir
        self.logger = logger
        self._lock = threading.Lock()
        self._thread = None
        self._stop = False
        self.latest_payload = {
            "ok": False,
            "title": "Planungsanzeige",
            "updated_at": None,
            "error": "Noch keine Daten geladen.",
            "show_grid": True,
            "font_scale": 1.0,
            "views": [],
        }

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.trigger_refresh("startup")

    def _loop(self):
        while not self._stop:
            s = self.settings_service.get()
            interval = max(30, int(s.get("refresh_interval_sec", 300)))
            time.sleep(interval)
            self._refresh_once()

    def trigger_refresh(self, reason="manual"):
        self.logger.info("Refresh: %s", reason)
        self._refresh_once()

    def _refresh_once(self):
        s = self.settings_service.get()
        with self._lock:
            try:
                share = s.get("share_link", "").strip()
                filename = s.get("selected_file", "").strip()
                if not share or not filename:
                    raise ValueError("Bitte Share-Link und Datei in /plansetup setzen")

                os.makedirs(self.cache_dir, exist_ok=True)
                xlsx = os.path.join(self.cache_dir, "current.xlsx")
                self.nextcloud_service.download_file(share, filename, xlsx)

                views = []
                for idx, v in enumerate([x for x in s.get("views", []) if x.get("active", True)]):
                    d = self.workbook_service.read_view(xlsx, v.get("sheet", ""), v.get("range", "A1:G12"))
                    views.append({
                        "id": idx,
                        "title": v.get("title", f"View {idx+1}"),
                        "duration_sec": max(5, int(v.get("duration_sec", 15))),
                        "sheet": d["sheet"],
                        "range": d["range"],
                        "rows": d["rows"],
                        "cells": d.get("cells", []),
                        "layout": d.get("layout", {}),
                        "theme_override": bool(v.get("theme_override", False)),
                    })

                self.latest_payload = {
                    "ok": True,
                    "title": s.get("title", "Planungsanzeige"),
                    "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    "error": "",
                    "show_grid": bool(s.get("show_grid", True)),
                    "font_scale": float(s.get("font_scale", 1.0)),
                    "views": views,
                }
            except Exception as exc:
                self.logger.error("Refresh fehlgeschlagen: %s", exc)
                self.latest_payload["error"] = str(exc)
                self.latest_payload["ok"] = len(self.latest_payload.get("views", [])) > 0

    def get_display_payload(self):
        with self._lock:
            return dict(self.latest_payload)
