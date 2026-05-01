from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BotConfig:
    telegram_bot_token: str
    telegram_admin_chat_id: int
    telegram_bot_username: str
    bot_data_dir: str
    bot_default_language: str
    bot_log_level: str
    bot_content_path: str


@dataclass
class BotSession:
    telegram_user_id: str
    language: str = "en"
    current_flow: str = "idle"
    current_step: str = "idle"
    draft_payload: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""


@dataclass
class LeadRecord:
    id: str
    timestamp: str
    telegram_user_id: str
    username: str
    full_name: str
    language: str
    company_or_role: str
    preferred_contact: str
    reason_for_contact: str
    source: str
    status: str


@dataclass
class FaqEntry:
    key: str
    keywords: list[str]
    answer_key: str


@dataclass
class ContentCatalog:
    labels: dict[str, str]
    answers: dict[str, str]
    prompts: dict[str, str]
    faq: list[FaqEntry]
