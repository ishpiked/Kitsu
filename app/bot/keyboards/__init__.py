from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.utils.constants import ButtonStyle, MAX_CALLBACK_DATA_LENGTH


def _create_button(
    text: str,
    callback_data: str | None = None,
    url: str | None = None,
    style: ButtonStyle = ButtonStyle.NEUTRAL,
) -> InlineKeyboardButton:
    if len(callback_data or "") > MAX_CALLBACK_DATA_LENGTH:
        raise ValueError(f"callback_data exceeds {MAX_CALLBACK_DATA_LENGTH} characters")

    if style == ButtonStyle.PRIMARY:
        text = f"🔵 {text}"
    elif style == ButtonStyle.SUCCESS:
        text = f"🟢 {text}"
    elif style == ButtonStyle.DANGER:
        text = f"🔴 {text}"
    elif style == ButtonStyle.NEUTRAL:
        text = f"⚪ {text}"

    if url:
        return InlineKeyboardButton(text, url=url)
    return InlineKeyboardButton(text, callback_data=callback_data or "")


def primary_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return _create_button(text, callback_data=callback_data, style=ButtonStyle.PRIMARY)


def success_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return _create_button(text, callback_data=callback_data, style=ButtonStyle.SUCCESS)


def danger_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return _create_button(text, callback_data=callback_data, style=ButtonStyle.DANGER)


def neutral_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return _create_button(text, callback_data=callback_data, style=ButtonStyle.NEUTRAL)


def url_button(text: str, url: str, style: ButtonStyle = ButtonStyle.NEUTRAL) -> InlineKeyboardButton:
    return _create_button(text, url=url, style=style)


def callback_button(text: str, callback_data: str, style: ButtonStyle = ButtonStyle.NEUTRAL) -> InlineKeyboardButton:
    return _create_button(text, callback_data=callback_data, style=style)


def build_keyboard(
    rows: list[list[InlineKeyboardButton]],
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(rows)


def create_single_button_keyboard(
    text: str,
    callback_data: str,
    style: ButtonStyle = ButtonStyle.NEUTRAL,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[callback_button(text, callback_data, style)]])


def create_two_button_keyboard(
    text1: str,
    callback_data1: str,
    text2: str,
    callback_data2: str,
    style1: ButtonStyle = ButtonStyle.NEUTRAL,
    style2: ButtonStyle = ButtonStyle.NEUTRAL,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [callback_button(text1, callback_data1, style1)],
        [callback_button(text2, callback_data2, style2)],
    ])