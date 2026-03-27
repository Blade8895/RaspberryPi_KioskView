import re
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote, urlparse

import requests
from bs4 import BeautifulSoup


class NextcloudService:
    def __init__(self, logger):
        self.logger = logger
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "RaspberryPi-KioskView/1.0"})

    def _extract_token(self, share_link: str):
        m = re.search(r"/s/([^/?#]+)", share_link)
        return m.group(1) if m else None

    def _list_xlsx_files_webdav(self, share_link: str):
        token = self._extract_token(share_link)
        if not token:
            return []

        p = urlparse(share_link)
        base_url = f"{p.scheme}://{p.netloc}"
        dav_url = f"{base_url}/public.php/dav/files/{token}/"

        r = self.s.request("PROPFIND", dav_url, timeout=15, headers={"Depth": "1"}, auth=(token, ""))
        r.raise_for_status()

        files = set()
        root = ET.fromstring(r.text)
        ns = {"d": "DAV:"}
        for response in root.findall("d:response", ns):
            href_el = response.find("d:href", ns)
            if href_el is None or not href_el.text:
                continue
            href = unquote(href_el.text)
            name = href.rstrip("/").split("/")[-1]
            if name.lower().endswith(".xlsx"):
                files.add(name)

        return sorted(files)

    def list_xlsx_files(self, share_link: str):
        try:
            files = self._list_xlsx_files_webdav(share_link)
            if files:
                return files
        except Exception as exc:
            self.logger.warning("WebDAV-Dateiliste konnte nicht geladen werden: %s", exc)

        files = set()
        try:
            r = self.s.get(share_link, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = unquote(a["href"])
                if ".xlsx" in href.lower():
                    name = href.split("/")[-1].split("?")[0]
                    if name.lower().endswith(".xlsx"):
                        files.add(name)
            for m in re.findall(r"([A-Za-z0-9 _\-\.\(\)]+\.xlsx)", soup.get_text(" ", strip=True), flags=re.IGNORECASE):
                files.add(m.strip())
        except Exception as exc:
            self.logger.warning("Dateiliste konnte nicht geladen werden: %s", exc)
        return sorted(files)

    def build_download_url(self, share_link: str, filename: str):
        token = self._extract_token(share_link)
        if not token:
            return None
        p = urlparse(share_link)
        encoded = quote(filename)
        return f"{p.scheme}://{p.netloc}/s/{token}/download?path=%2F&files={encoded}"

    def _build_webdav_file_url(self, share_link: str, filename: str):
        token = self._extract_token(share_link)
        if not token:
            return None, None
        p = urlparse(share_link)
        encoded = quote(filename, safe="")
        url = f"{p.scheme}://{p.netloc}/public.php/dav/files/{token}/{encoded}"
        return url, token

    def _download_stream_to_path(self, response, target_path: str):
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def _looks_like_xlsx(self, target_path: str):
        try:
            with open(target_path, "rb") as f:
                return f.read(2) == b"PK"
        except Exception:
            return False

    def download_file(self, share_link: str, filename: str, target_path: str):
        webdav_url, token = self._build_webdav_file_url(share_link, filename)
        if not webdav_url:
            raise ValueError("Ungültiger Share-Link")

        # Bevorzugt über Public WebDAV laden (zuverlässig bei öffentlichen Shares)
        try:
            r = self.s.get(webdav_url, timeout=30, stream=True, auth=(token, ""))
            r.raise_for_status()
            self._download_stream_to_path(r, target_path)
            if self._looks_like_xlsx(target_path):
                return target_path
            self.logger.warning("WebDAV-Download ist kein XLSX-Archiv, nutze Fallback-Link.")
        except Exception as exc:
            self.logger.warning("WebDAV-Download fehlgeschlagen: %s", exc)

        # Fallback auf klassischen Share-Download-Link
        fallback_url = self.build_download_url(share_link, filename)
        r = self.s.get(fallback_url, timeout=30, stream=True)
        r.raise_for_status()
        self._download_stream_to_path(r, target_path)
        if not self._looks_like_xlsx(target_path):
            raise ValueError("Geladene Datei ist kein gültiges XLSX-Archiv")
        return target_path
