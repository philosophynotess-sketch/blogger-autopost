from datetime import date

from config.settings import CAT_ANIMALS, CAT_DAILY, CAT_SEO, CAT_STARS
from content.schedule import resolve_slot


def test_monday_is_daily():
    slot = resolve_slot(date(2026, 7, 20))  # Monday
    assert slot.category_id == CAT_DAILY
    assert slot.needs_image is False
    assert slot.label == "오늘의 운세"


def test_tuesday_animals():
    slot = resolve_slot(date(2026, 7, 21))
    assert slot.category_id == CAT_ANIMALS


def test_wednesday_stars():
    slot = resolve_slot(date(2026, 7, 22))
    assert slot.category_id == CAT_STARS


def test_sunday_seo():
    slot = resolve_slot(date(2026, 7, 26))  # Sunday
    assert slot.category_id == CAT_SEO
    assert slot.needs_image is True
    assert slot.label == "운세 가이드"


def test_force_category():
    slot = resolve_slot(date(2026, 7, 20), force_category=CAT_SEO)
    assert slot.category_id == CAT_SEO
    assert slot.needs_image is True


def test_date_ko_format():
    slot = resolve_slot(date(2026, 7, 22))
    assert slot.date_ko == "2026년 7월 22일"
