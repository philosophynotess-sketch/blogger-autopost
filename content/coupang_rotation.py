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


def pick_coupang_link(post_date: date, links: list[str] | None = None) -> str:
    """
    One link per day. Within each round of len(links) days every URL is used
    exactly once (shuffled by round). After a full cycle, reshuffle for the
    next round. Deterministic for the same date (CI-friendly, no state file).
    """
    pool = links if links is not None else load_coupang_links()
    n = len(pool)
    day_index = post_date.toordinal()
    round_num = day_index // n
    pos = day_index % n

    order = pool.copy()
    random.Random(round_num).shuffle(order)
    return order[pos]
