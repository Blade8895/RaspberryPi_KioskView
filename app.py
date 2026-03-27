import os
from flask import Flask, render_template, request, jsonify, redirect, url_for

from services.logger_service import get_logger
from services.settings_service import SettingsService
from services.nextcloud_service import NextcloudService
from services.workbook_service import WorkbookService
from services.updater_service import UpdaterService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
CACHE_DIR = os.path.join(BASE_DIR, "downloads", "cache")
LOG_DIR = os.path.join(BASE_DIR, "logs")

app = Flask(__name__)
logger = get_logger(LOG_DIR)
settings_service = SettingsService(SETTINGS_PATH, logger)
nextcloud_service = NextcloudService(logger)
workbook_service = WorkbookService(logger)
updater_service = UpdaterService(settings_service, nextcloud_service, workbook_service, CACHE_DIR, logger)


def _to_int(v, default):
    try:
        return int(v)
    except Exception:
        return default


def _to_float(v, default):
    try:
        return float(v)
    except Exception:
        return default


@app.route("/")
def display():
    return render_template("display.html")


@app.route("/api/display-data")
def api_display_data():
    return jsonify(updater_service.get_display_payload())


@app.route("/api/files")
def api_files():
    share_link = request.args.get("share_link", "").strip()
    files = nextcloud_service.list_xlsx_files(share_link) if share_link else []
    return jsonify({"files": files})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    updater_service.trigger_refresh("manual")
    return jsonify({"ok": True})


@app.route("/plansetup", methods=["GET", "POST"])
def plansetup():
    if request.method == "POST":
        s = settings_service.get()
        s["share_link"] = request.form.get("share_link", "").strip()
        s["selected_file"] = request.form.get("selected_file", "").strip()
        s["refresh_interval_sec"] = _to_int(request.form.get("refresh_interval_sec", 300), 300)
        s["font_scale"] = _to_float(request.form.get("font_scale", 1.0), 1.0)
        s["show_grid"] = request.form.get("show_grid") == "on"
        s["title"] = request.form.get("title", "Planungsanzeige").strip() or "Planungsanzeige"

        import json
        try:
            views = json.loads(request.form.get("views_json", "[]"))
            if isinstance(views, list) and views:
                s["views"] = views
        except Exception:
            logger.warning("views_json ungültig")

        settings_service.save(s)
        updater_service.trigger_refresh("settings_changed")
        return redirect(url_for("plansetup"))

    s = settings_service.get()
    files = nextcloud_service.list_xlsx_files(s.get("share_link", "")) if s.get("share_link") else []
    return render_template("setup.html", settings=s, files=files)


if __name__ == "__main__":
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    updater_service.start()
    app.run(host="0.0.0.0", port=5000)
