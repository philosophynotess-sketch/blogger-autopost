"""Map calendar date to a fortune post category slot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from config.settings import (
    CAT_SEO,
    CATEGORY_LABELS,
    WEEKDAY_ROTATION,
)

SEOUL = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class PostSlot:
    category_id: str
    label: str
    post_date: date
    needs_image: bool

    @property
    def date_ko(self) -> str:
        return f"{self.post_date.year}년 {self.post_date.month}월 {self.post_date.day}일"

    @property
    def date_iso(self) -> str:
        return self.post_date.isoformat()


def today_seoul(now: datetime | None = None) -> date:
    if now is None:
        now = datetime.now(SEOUL)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=SEOUL)
    else:
        now = now.astimezone(SEOUL)
    return now.date()


def resolve_slot(
    post_date: date | None = None,
    force_category: str | None = None,
) -> PostSlot:
    """Return the post slot for a given Seoul calendar date."""
    if post_date is None:
        post_date = today_seoul()

    if force_category:
        category_id = force_category
    else:
        category_id = WEEKDAY_ROTATION[post_date.weekday()]

    label = CATEGORY_LABELS[category_id]
    needs_image = category_id == CAT_SEO
    return PostSlot(
        category_id=category_id,
        label=label,
        post_date=post_date,
        needs_image=needs_image,
    )
