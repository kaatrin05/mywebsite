from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import BotSession, LeadRecord


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class JsonFileStore:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_path = self.base_dir / "sessions.json"
        self.leads_path = self.base_dir / "leads.json"
        self.log_path = self.base_dir / "log.jsonl"
        self._ensure_json_array(self.sessions_path)
        self._ensure_json_array(self.leads_path)

    def get_session(self, telegram_user_id: str, default_language: str) -> BotSession:
        rows = self._read_array(self.sessions_path)
        for row in rows:
            if row.get("telegram_user_id") == telegram_user_id:
                return BotSession(**row)
        session = BotSession(
            telegram_user_id=telegram_user_id,
            language=default_language,
            updated_at=utc_now_iso(),
        )
        self.save_session(session)
        return session

    def save_session(self, session: BotSession) -> None:
        rows = self._read_array(self.sessions_path)
        payload = asdict(session)
        payload["updated_at"] = utc_now_iso()
        replaced = False
        for index, row in enumerate(rows):
            if row.get("telegram_user_id") == session.telegram_user_id:
                rows[index] = payload
                replaced = True
                break
        if not replaced:
            rows.append(payload)
        self._write_array(self.sessions_path, rows)

    def reset_session(self, telegram_user_id: str, default_language: str) -> BotSession:
        session = BotSession(
            telegram_user_id=telegram_user_id,
            language=default_language,
            updated_at=utc_now_iso(),
        )
        self.save_session(session)
        return session

    def add_lead(self, lead_input: dict[str, Any]) -> LeadRecord:
        rows = self._read_array(self.leads_path)
        lead = LeadRecord(
            id=str(uuid.uuid4()),
            timestamp=utc_now_iso(),
            telegram_user_id=str(lead_input.get("telegram_user_id", "")),
            username=str(lead_input.get("username", "")),
            full_name=str(lead_input.get("full_name", "")),
            language=str(lead_input.get("language", "en")),
            company_or_role=str(lead_input.get("company_or_role", "")),
            preferred_contact=str(lead_input.get("preferred_contact", "")),
            reason_for_contact=str(lead_input.get("reason_for_contact", "")),
            source=str(lead_input.get("source", "telegram_bot")),
            status=str(lead_input.get("status", "new")),
        )
        rows.append(asdict(lead))
        self._write_array(self.leads_path, rows)
        return lead

    def append_log(self, event: dict[str, Any]) -> None:
        payload = dict(event)
        payload.setdefault("timestamp", utc_now_iso())
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _ensure_json_array(self, path: Path) -> None:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return
            except json.JSONDecodeError:
                pass
        self._write_array(path, [])

    def _read_array(self, path: Path) -> list[dict[str, Any]]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self._write_array(path, [])
            return []

    def _write_array(self, path: Path, rows: list[dict[str, Any]]) -> None:
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(path)
