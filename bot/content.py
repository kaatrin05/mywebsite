from __future__ import annotations

import json
from pathlib import Path

from .models import ContentCatalog, FaqEntry


class ContentStore:
    def __init__(self, content_path: str) -> None:
        self._path = Path(content_path)
        self._raw = self._load()

    def catalog(self, language: str) -> ContentCatalog:
        lang = language if language in self._raw else "en"
        item = self._raw[lang]
        faq = [FaqEntry(**entry) for entry in item["faq"]]
        return ContentCatalog(
            labels=item["labels"],
            answers=item["answers"],
            prompts=item["prompts"],
            faq=faq,
        )

    def bot_url(self, username: str) -> str:
        clean = username.strip().lstrip("@")
        return f"https://t.me/{clean}" if clean else "https://t.me/"

    def _load(self) -> dict:
        with self._path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
