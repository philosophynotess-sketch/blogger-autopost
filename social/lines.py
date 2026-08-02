"""Build 12 one-line social captions from post content or Gemini."""

from __future__ import annotations

import re
from typing import Any

import requests

from config.settings import CAT_ANIMALS, CAT_STARS, Settings
from content.schedule import PostSlot
from social.characters import ANIMAL_LABELS, STAR_LABELS


def _clean_line(text: str, max_len: int = 28) -> str:
    t = re.sub(r"<[^>]+>", "", text)
    t = re.sub(r"\s+", " ", t).strip(" -·•|")
    if len(t) > max_len:
        t = t[: max_len - 1].rstrip() + "…"
    return t


def extract_lines_from_html(body_html: str, labels: list[str]) -> list[str]:
    """Best-effort parse of 12 cards from blog HTML (f-z-card blocks)."""
    blocks = re.findall(
        r'<div class="f-z-card"[^>]*>.*?</div>',
        body_html,
        flags=re.I | re.S,
    )
    lines: list[str] = []
    for block in blocks:
        # prefer keyword line
        kw = re.search(r'class="f-keyword"[^>]*>(.*?)</p>', block, flags=re.I | re.S)
        if kw:
            lines.append(_clean_line(kw.group(1)))
            continue
        ps = re.findall(r"<p[^>]*>(.*?)</p>", block, flags=re.I | re.S)
        plain = [_clean_line(p) for p in ps if _clean_line(p)]
        if plain:
            # skip if looks like label only
            lines.append(plain[-1] if len(plain[-1]) > 4 else plain[0])
    # pad/truncate to 12
    while len(lines) < 12:
        lines.append("오늘은 페이스 조절이 답이 되는 날")
    return lines[:12]


def generate_lines_with_gemini(
    settings: Settings,
    slot: PostSlot,
    labels: list[str],
) -> list[str]:
    """Ask Gemini for exactly 12 short SNS lines."""
    kind = "띠" if slot.category_id == CAT_ANIMALS else "별자리"
    label_blob = ", ".join(labels)
    prompt = f"""당신은 한국어 SNS 운세 카드 카피라이터입니다.
날짜: {slot.date_ko}
종류: {kind} 12개 한 줄 운세

각 항목에 대해 15~24자 내외 한 줄 조언만 작성하세요.
긍정적이되 단정 금지. 의료/투자 보장 금지.
이모지 금지. 번호/이름 없이 조언 문장만.

순서 고정 ({label_blob}):
출력 형식 — 정확히 12줄, 줄마다 한 문장만:
1. ...
2. ...
...
12. ...
"""
    url = settings.gemini_url
    payload: dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024},
    }
    res = requests.post(url, json=payload, timeout=90)
    res.raise_for_status()
    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    raw_lines = []
    for line in str(text).splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d+[\.)]\s*", "", line)
        line = re.sub(r"^[-*]\s*", "", line)
        if line:
            raw_lines.append(_clean_line(line, 30))
    while len(raw_lines) < 12:
        raw_lines.append("오늘은 무리보다 리듬이 중요한 날")
    return raw_lines[:12]


def resolve_social_lines(
    settings: Settings,
    slot: PostSlot,
    body_html: str,
) -> list[str]:
    labels = (
        ANIMAL_LABELS
        if slot.category_id == CAT_ANIMALS
        else STAR_LABELS
        if slot.category_id == CAT_STARS
        else []
    )
    if not labels:
        return []
    # Prefer dedicated short-copy call for denser SNS quality
    try:
        return generate_lines_with_gemini(settings, slot, labels)
    except Exception as e:
        print(f"⚠️ SNS 한 줄 생성 실패, HTML 추출 폴백: {e}")
        return extract_lines_from_html(body_html, labels)
