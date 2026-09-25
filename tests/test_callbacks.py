import pytest
from app.bot.callbacks import create_callback, parse_callback, CallbackData


def test_create_callback():
    data = create_callback("anime", "view", "123")
    assert data == "anime:view:123"


def test_create_callback_with_extra():
    data = create_callback("library", "page", "2", "watching")
    assert data == "library:page:2:watching"


def test_create_callback_no_identifier():
    data = create_callback("nav", "back")
    assert data == "nav:back"


def test_parse_callback():
    parsed = parse_callback("anime:view:123")
    assert parsed.prefix == "anime"
    assert parsed.action == "view"
    assert parsed.identifier == "123"
    assert parsed.extra is None


def test_parse_callback_with_extra():
    parsed = parse_callback("library:page:2:watching")
    assert parsed.prefix == "library"
    assert parsed.action == "page"
    assert parsed.identifier == "2"
    assert parsed.extra == "watching"


def test_parse_callback_no_identifier():
    parsed = parse_callback("nav:back")
    assert parsed.prefix == "nav"
    assert parsed.action == "back"
    assert parsed.identifier is None
    assert parsed.extra is None


def test_callback_roundtrip():
    original = create_callback("anime", "add", "456", "plan_to_watch")
    parsed = parse_callback(original)
    assert parsed.prefix == "anime"
    assert parsed.action == "add"
    assert parsed.identifier == "456"
    assert parsed.extra == "plan_to_watch"


def test_invalid_callback():
    with pytest.raises(ValueError):
        parse_callback("invalid")


def test_callback_max_length():
    with pytest.raises(ValueError):
        create_callback("a" * 50, "b" * 50)