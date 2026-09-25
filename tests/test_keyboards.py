import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.bot.keyboards import (
    primary_button,
    success_button,
    danger_button,
    neutral_button,
    url_button,
    callback_button,
    build_keyboard,
    create_single_button_keyboard,
    create_two_button_keyboard,
)
from app.utils.constants import ButtonStyle, MAX_CALLBACK_DATA_LENGTH


def test_primary_button():
    btn = primary_button("Test", "test:action")
    assert isinstance(btn, InlineKeyboardButton)
    assert btn.text == "🔵 Test"
    assert btn.callback_data == "test:action"


def test_success_button():
    btn = success_button("Test", "test:action")
    assert btn.text == "🟢 Test"
    assert btn.callback_data == "test:action"


def test_danger_button():
    btn = danger_button("Test", "test:action")
    assert btn.text == "🔴 Test"
    assert btn.callback_data == "test:action"


def test_neutral_button():
    btn = neutral_button("Test", "test:action")
    assert btn.text == "⚪ Test"
    assert btn.callback_data == "test:action"


def test_url_button():
    btn = url_button("Test", "https://example.com")
    assert btn.text == "⚪ Test"
    assert btn.url == "https://example.com"


def test_callback_button_with_style():
    btn = callback_button("Test", "test:action", style=ButtonStyle.SUCCESS)
    assert btn.text == "🟢 Test"
    assert btn.callback_data == "test:action"


def test_build_keyboard():
    rows = [[primary_button("A", "a"), success_button("B", "b")], [danger_button("C", "c")]]
    markup = build_keyboard(rows)
    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 2
    assert len(markup.inline_keyboard[0]) == 2
    assert len(markup.inline_keyboard[1]) == 1


def test_create_single_button_keyboard():
    markup = create_single_button_keyboard("Test", "test:action", ButtonStyle.PRIMARY)
    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1
    assert markup.inline_keyboard[0][0].text == "🔵 Test"


def test_create_two_button_keyboard():
    markup = create_two_button_keyboard("A", "a", "B", "b", ButtonStyle.PRIMARY, ButtonStyle.DANGER)
    assert len(markup.inline_keyboard) == 2
    assert markup.inline_keyboard[0][0].text == "🔵 A"
    assert markup.inline_keyboard[1][0].text == "🔴 B"


def test_callback_data_too_long():
    with pytest.raises(ValueError):
        primary_button("Test", "a" * (MAX_CALLBACK_DATA_LENGTH + 1))