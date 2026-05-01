from __future__ import annotations

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .keyboards import contact_confirm_keyboard, language_keyboard, main_menu_keyboard
from .matcher import match_answer_key
from .models import BotSession, ContentCatalog
from .services import BotServices


FLOW_CONTACT = "contact"
STEP_NAME = "name"
STEP_COMPANY = "company"
STEP_CONTACT = "preferred_contact"
STEP_REASON = "reason"
STEP_CONFIRM = "confirm"


def register_handlers(application: Application, services: BotServices) -> None:
    application.bot_data["services"] = services
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))


def _services(context: ContextTypes.DEFAULT_TYPE) -> BotServices:
    return context.application.bot_data["services"]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    session = services.get_session(update.effective_user)
    session.current_flow = "language"
    session.current_step = "select_language"
    session.draft_payload = {}
    services.save_session(session)
    await update.effective_message.reply_text(
        "Choose language / Выберите язык",
        reply_markup=language_keyboard(),
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_main_menu(update, context)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    session = services.get_session(update.effective_user)
    session.current_flow = "language"
    session.current_step = "select_language"
    services.save_session(session)
    await update.effective_message.reply_text(
        "Choose language / Выберите язык",
        reply_markup=language_keyboard(),
    )


async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    session = services.get_session(update.effective_user)
    catalog = services.content_for(session.language)
    session.current_flow = FLOW_CONTACT
    session.current_step = STEP_NAME
    session.draft_payload = {}
    services.save_session(session)
    await update.effective_message.reply_text(
        catalog.prompts["contact.ask_name"],
        reply_markup=main_menu_keyboard(catalog),
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    session = services.get_session(update.effective_user)
    session.current_flow = "idle"
    session.current_step = "idle"
    session.draft_payload = {}
    services.save_session(session)
    catalog = services.content_for(session.language)
    await update.effective_message.reply_text(
        catalog.prompts["flow.cancelled"],
        reply_markup=main_menu_keyboard(catalog),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    session = services.get_session(update.effective_user)
    catalog = services.content_for(session.language)
    await update.effective_message.reply_text(
        catalog.prompts["help"],
        reply_markup=main_menu_keyboard(catalog),
    )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    user = update.effective_user
    message = update.effective_message.text.strip()
    session = services.get_session(user)

    if _is_language_choice(message):
        await apply_language_choice(update, context, session, message.lower())
        return

    catalog = services.content_for(session.language)
    action = map_menu_action(catalog, message)

    if action == "menu.home":
        await show_main_menu(update, context)
        return
    if action == "menu.cancel":
        await cancel_command(update, context)
        return
    if action == "menu.language":
        await language_command(update, context)
        return
    if action == "menu.contact":
        await contact_command(update, context)
        return
    if action == "menu.ask":
        await update.effective_message.reply_text(
            catalog.prompts["faq.ask"],
            reply_markup=main_menu_keyboard(catalog),
        )
        return

    if session.current_flow == FLOW_CONTACT:
        await handle_contact_flow(update, context, session, message)
        return

    answer_key = map_answer_action(action) if action else match_answer_key(catalog, message)
    if answer_key:
        await update.effective_message.reply_text(
            catalog.answers[answer_key],
            reply_markup=main_menu_keyboard(catalog),
        )
        return

    await update.effective_message.reply_text(
        catalog.prompts["faq.fallback"],
        reply_markup=main_menu_keyboard(catalog),
    )


async def apply_language_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: BotSession,
    language: str,
) -> None:
    services = _services(context)
    session.language = "ru" if language.startswith("ru") else "en"
    session.current_flow = "idle"
    session.current_step = "idle"
    services.save_session(session)
    catalog = services.content_for(session.language)
    await update.effective_message.reply_text(
        catalog.prompts["welcome"],
        reply_markup=main_menu_keyboard(catalog),
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = _services(context)
    session = services.get_session(update.effective_user)
    session.current_flow = "idle"
    session.current_step = "idle"
    services.save_session(session)
    catalog = services.content_for(session.language)
    await update.effective_message.reply_text(
        catalog.prompts["menu"],
        reply_markup=main_menu_keyboard(catalog),
    )


async def handle_contact_flow(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: BotSession,
    message: str,
) -> None:
    services = _services(context)
    catalog = services.content_for(session.language)
    if session.current_step == STEP_NAME:
        session.draft_payload["full_name"] = message
        session.current_step = STEP_COMPANY
        services.save_session(session)
        await update.effective_message.reply_text(catalog.prompts["contact.ask_company"])
        return
    if session.current_step == STEP_COMPANY:
        session.draft_payload["company_or_role"] = message
        session.current_step = STEP_CONTACT
        services.save_session(session)
        await update.effective_message.reply_text(catalog.prompts["contact.ask_contact"])
        return
    if session.current_step == STEP_CONTACT:
        session.draft_payload["preferred_contact"] = message
        session.current_step = STEP_REASON
        services.save_session(session)
        await update.effective_message.reply_text(catalog.prompts["contact.ask_reason"])
        return
    if session.current_step == STEP_REASON:
        session.draft_payload["reason_for_contact"] = message
        session.current_step = STEP_CONFIRM
        services.save_session(session)
        summary = catalog.prompts["contact.summary"].format(
            full_name=session.draft_payload["full_name"],
            company_or_role=session.draft_payload["company_or_role"],
            preferred_contact=session.draft_payload["preferred_contact"],
            reason_for_contact=session.draft_payload["reason_for_contact"],
        )
        await update.effective_message.reply_text(
            summary,
            reply_markup=contact_confirm_keyboard(catalog),
        )
        return
    if session.current_step == STEP_CONFIRM:
        confirm_label = catalog.labels["contact.confirm"]
        edit_label = catalog.labels["contact.edit"]
        if message == confirm_label:
            lead = services.save_lead(session, update.effective_user)
            try:
                await context.bot.send_message(
                    chat_id=services.config.telegram_admin_chat_id,
                    text=services.admin_message(lead),
                    reply_markup=ReplyKeyboardRemove(),
                )
            except Exception as error:  # pragma: no cover
                services.log_event({"level": "error", "message": "admin_notify_failed", "error": str(error)})
            session.current_flow = "idle"
            session.current_step = "idle"
            session.draft_payload = {}
            services.save_session(session)
            await update.effective_message.reply_text(
                catalog.prompts["contact.submitted"],
                reply_markup=main_menu_keyboard(catalog),
            )
            return
        if message == edit_label:
            session.current_step = STEP_NAME
            session.draft_payload = {}
            services.save_session(session)
            await update.effective_message.reply_text(
                catalog.prompts["contact.ask_name"],
                reply_markup=main_menu_keyboard(catalog),
            )
            return

    await update.effective_message.reply_text(
        catalog.prompts["contact.retry"],
        reply_markup=contact_confirm_keyboard(catalog) if session.current_step == STEP_CONFIRM else main_menu_keyboard(catalog),
    )


def _is_language_choice(message: str) -> bool:
    lowered = message.lower()
    return lowered in {"ru", "en", "русский", "english"}


def map_menu_action(catalog: ContentCatalog, message: str) -> str | None:
    for key, label in catalog.labels.items():
        if message == label:
            return key
    return None


def map_answer_action(action: str | None) -> str | None:
    mapping = {
        "menu.about": "about",
        "menu.skills": "skills",
        "menu.experience": "experience",
        "menu.availability": "availability",
        "menu.cv": "cv",
    }
    return mapping.get(action or "")
