from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from .models import BotConfig


def load_config() -> BotConfig:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")
    if not admin_chat_id:
        raise RuntimeError("Missing TELEGRAM_ADMIN_CHAT_ID")

    default_language = os.getenv("BOT_DEFAULT_LANGUAGE", "en").strip().lower() or "en"
    if default_language not in {"en", "ru"}:
        raise RuntimeError("BOT_DEFAULT_LANGUAGE must be 'en' or 'ru'")

    return BotConfig(
        telegram_bot_token=token,
        telegram_admin_chat_id=int(admin_chat_id),
        telegram_bot_username=os.getenv("TELEGRAM_BOT_USERNAME", "kaatrin_portfolio_bot").strip(),
        bot_data_dir=os.getenv("BOT_DATA_DIR", "./data").strip() or "./data",
        bot_default_language=default_language,
        bot_log_level=os.getenv("BOT_LOG_LEVEL", "INFO").strip().upper() or "INFO",
        bot_content_path=os.getenv(
            "BOT_CONTENT_PATH",
            str(Path(__file__).resolve().parent / "content" / "portfolio_content.json"),
        ).strip(),
    )
