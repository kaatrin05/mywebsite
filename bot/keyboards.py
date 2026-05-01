from __future__ import annotations

from telegram import KeyboardButton, ReplyKeyboardMarkup

from .models import ContentCatalog


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("RU"), KeyboardButton("EN")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_keyboard(content: ContentCatalog) -> ReplyKeyboardMarkup:
    labels = content.labels
    rows = [
        [labels["menu.about"], labels["menu.skills"]],
        [labels["menu.experience"], labels["menu.availability"]],
        [labels["menu.contact"], labels["menu.ask"]],
        [labels["menu.cv"], labels["menu.language"]],
        [labels["menu.home"], labels["menu.cancel"]],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def contact_confirm_keyboard(content: ContentCatalog) -> ReplyKeyboardMarkup:
    labels = content.labels
    return ReplyKeyboardMarkup(
        [[labels["contact.confirm"], labels["contact.edit"]], [labels["menu.cancel"]]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
