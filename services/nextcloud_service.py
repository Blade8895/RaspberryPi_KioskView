import re
from urllib.parse import unquote, urlparse

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

    def list_xlsx_files(self, share_link: str):
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
        return f"{p.scheme}://{p.netloc}/s/{token}/download?path=%2F&files={filename}"

    def download_file(self, share_link: str, filename: str, target_path: str):
        url = self.build_download_url(share_link, filename)
        if not url:
            raise ValueError("Ungültiger Share-Link")
        r = self.s.get(url, timeout=30, stream=True)
        r.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return target_path
