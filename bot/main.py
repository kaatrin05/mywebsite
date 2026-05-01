from __future__ import annotations

import logging

from telegram.ext import ApplicationBuilder

from .config import load_config
from .handlers import register_handlers
from .services import BotServices


def main() -> None:
    config = load_config()
    logging.basicConfig(
        level=getattr(logging, config.bot_log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    services = BotServices(config)
    application = ApplicationBuilder().token(config.telegram_bot_token).build()
    register_handlers(application, services)
    application.run_polling(drop_pending_updates=True)
