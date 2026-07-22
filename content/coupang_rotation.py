"""Rotate Coupang Partners links without replacement per round (date-based)."""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path

LINKS_PATH = Path(__file__).resolve().parent / "coupang_links.json"

# Official Coupang Partners disclosure (required on every post with partners links)
COUPANG_DISCLOSURE = (
    "이 포스팅은 쿠팡 파트너스 활동의 일환으로, "
    "이에 따른 일정액의 수수료를 제공받습니다."
)


def load_coupang_links(path: Path | None = None) -> list[str]:
    p = path or LINKS_PATH
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise RuntimeError("coupang_links.json 이 비어 있거나 형식이 잘못되었습니다.")
    # preserve order, drop empties/dupes
    seen: set[str] = set()
    links: list[str] = []
    for item in data:
        url = str(item).strip()
        if url and url not in seen:
            seen.add(url)
            links.append(url)
    if not links:
        raise RuntimeError("유효한 쿠팡 파트너스 링크가 없습니다.")
    return links


def pick_coupang_link(
    post_date: date,
    links: list[str] | None = None,
    *,
    offset: int = 0,
) -> str:
    """
    Deterministic link pick for a calendar day (+ optional offset).

    Within each round of len(links) days every URL is used once (shuffled by
    round). offset=1 yields a different slot than offset=0 on the same day
    (for mid-post vs footer links).
    """
    pool = links if links is not None else load_coupang_links()
    n = len(pool)
    day_index = post_date.toordinal() + int(offset)
    round_num = day_index // n
    pos = day_index % n

    order = pool.copy()
    random.Random(round_num).shuffle(order)
    return order[pos]


def pick_coupang_pair(post_date: date, links: list[str] | None = None) -> tuple[str, str]:
    """Return (mid_link, footer_link), always different when pool has 2+ URLs."""
    pool = links if links is not None else load_coupang_links()
    mid = pick_coupang_link(post_date, pool, offset=0)
    footer = pick_coupang_link(post_date, pool, offset=1)
    if footer == mid and len(pool) > 1:
        footer = pick_coupang_link(post_date, pool, offset=2)
    return mid, footer
