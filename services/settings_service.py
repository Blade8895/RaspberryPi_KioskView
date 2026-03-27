import copy
import json
import os


DEFAULT_SETTINGS = {
    "share_link": "",
    "selected_file": "",
    "refresh_interval_sec": 300,
    "font_scale": 1.0,
    "show_grid": True,
    "title": "Planungsanzeige",
    "views": [
        {"title": "Woche", "sheet": "Woche", "range": "A1:G12", "duration_sec": 20, "active": True},
        {"title": "Urlaub", "sheet": "Urlaub", "range": "A1:G20", "duration_sec": 20, "active": True},
    ],
}


class SettingsService:
    def __init__(self, path: str, logger):
        self.path = path
        self.logger = logger
        self._settings = copy.deepcopy(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            self.save(DEFAULT_SETTINGS)
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._settings = self._merge(data)
        except Exception as exc:
            self.logger.error("settings laden fehlgeschlagen: %s", exc)
            self._settings = copy.deepcopy(DEFAULT_SETTINGS)
            self.save(self._settings)

    def _merge(self, data):
        merged = copy.deepcopy(DEFAULT_SETTINGS)
        if isinstance(data, dict):
            for k in merged:
                if k in data:
                    merged[k] = data[k]
        if not isinstance(merged.get("views"), list):
            merged["views"] = copy.deepcopy(DEFAULT_SETTINGS["views"])
        return merged

    def get(self):
        return copy.deepcopy(self._settings)

    def save(self, settings):
        self._settings = self._merge(settings)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)
