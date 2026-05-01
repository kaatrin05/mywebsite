from __future__ import annotations

from dataclasses import asdict

from telegram import User

from .content import ContentStore
from .models import BotConfig, BotSession, ContentCatalog, LeadRecord
from .storage import JsonFileStore


class BotServices:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.storage = JsonFileStore(config.bot_data_dir)
        self.content = ContentStore(config.bot_content_path)

    def get_session(self, user: User) -> BotSession:
        return self.storage.get_session(str(user.id), self.config.bot_default_language)

    def save_session(self, session: BotSession) -> None:
        self.storage.save_session(session)

    def reset_session(self, user: User) -> BotSession:
        return self.storage.reset_session(str(user.id), self.config.bot_default_language)

    def content_for(self, language: str) -> ContentCatalog:
        return self.content.catalog(language)

    def save_lead(self, session: BotSession, user: User) -> LeadRecord:
        payload = dict(session.draft_payload)
        payload.update(
            {
                "telegram_user_id": str(user.id),
                "username": user.username or "",
                "language": session.language,
                "source": "telegram_bot",
                "status": "new",
            }
        )
        return self.storage.add_lead(payload)

    def log_event(self, event: dict) -> None:
        self.storage.append_log(event)

    def admin_message(self, lead: LeadRecord) -> str:
        username_line = f"@{lead.username}" if lead.username else "(none)"
        return (
            "New portfolio lead\n\n"
            f"Time: {lead.timestamp}\n"
            f"Name: {lead.full_name}\n"
            f"Username: {username_line}\n"
            f"User ID: {lead.telegram_user_id}\n"
            f"Language: {lead.language}\n"
            f"Company/Role: {lead.company_or_role}\n"
            f"Preferred Contact: {lead.preferred_contact}\n"
            f"Reason: {lead.reason_for_contact}\n"
            f"Status: {lead.status}"
        )
