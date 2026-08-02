"""Build social assets (cards + captions) for a blog post day."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from config.settings import CAT_ANIMALS, CAT_DAILY, CAT_SEO, CAT_STARS, Settings
from content.schedule import PostSlot
from social.card_renderer import (
    render_animal_card,
    render_daily_carousel,
    render_star_card,
)
from social.lines import resolve_social_lines

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "docs" / "social" / "out"


def blog_url_for_day(post_date: date, base: str = "https://unseinsight.blogspot.com/") -> str:
    # Blogger post URLs vary; home + date hint until search/slug available
    return base.rstrip("/") + "/"


def build_caption(
    *,
    slot: PostSlot,
    blog_url: str,
    lines: list[str] | None = None,
) -> str:
    title = f"{slot.date_ko} {slot.label}"
    hook = ""
    if lines:
        hook = lines[0]
    return f"""{title} 🃏

{hook}

한 줄만 보고 넘기지 마세요.
시간대·영역별 상세 운세는 블로그에 있어요.

🔗 {blog_url}

#오늘의운세 #띠별운세 #별자리운세 #운세인사이트 #{slot.post_date.month}월운세
""".strip()


def generate_social_assets(
    settings: Settings,
    slot: PostSlot,
    body_html: str,
    *,
    out_dir: Path | None = None,
    blog_url: str | None = None,
) -> Path:
    """
    Write cards + caption under docs/social/out/YYYY-MM-DD/
    Returns output directory.
    """
    out = out_dir or (DEFAULT_OUT / slot.date_iso)
    out.mkdir(parents=True, exist_ok=True)
    url = blog_url or blog_url_for_day(slot.post_date)
    lines = resolve_social_lines(settings, slot, body_html)

    paths: list[str] = []
    if slot.category_id == CAT_ANIMALS and lines:
        p = out / "feed-animals.png"
        render_animal_card(slot.post_date, lines, out_path=p)
        paths.append(p.name)
    elif slot.category_id == CAT_STARS and lines:
        p = out / "feed-stars.png"
        render_star_card(slot.post_date, lines, out_path=p)
        paths.append(p.name)
    elif slot.category_id in (CAT_DAILY, CAT_SEO):
        # 3-slide style summary carousel from soft defaults + body snippets
        slides = _daily_slides(slot, body_html)
        names = render_daily_carousel(slot.post_date, slides, out_dir=out)
        paths.extend(names)

    caption = build_caption(slot=slot, blog_url=url, lines=lines)
    (out / "caption.txt").write_text(caption, encoding="utf-8")
    (out / "threads.txt").write_text(
        caption + "\n\n(스레드: 이미지 1장 + 위 텍스트)",
        encoding="utf-8",
    )
    meta = {
        "date": slot.date_iso,
        "category": slot.category_id,
        "label": slot.label,
        "blog_url": url,
        "files": paths,
        "lines": lines,
    }
    (out / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"📱 소셜 에셋 저장: {out} ({', '.join(paths) or 'caption only'})")
    return out


def _daily_slides(slot: PostSlot, body_html: str) -> list[dict[str, str]]:
    import re

    plain = re.sub(r"<[^>]+>", " ", body_html)
    plain = re.sub(r"\s+", " ", plain).strip()
    snippet = plain[:80] + ("…" if len(plain) > 80 else "")
    return [
        {
            "title": f"{slot.date_ko}",
            "body": f"{slot.label}\n오늘의 한 줄",
            "sub": snippet[:40] or "페이스 조절이 답이 되는 날",
        },
        {
            "title": "핵심만 콕",
            "body": "시간대 · 애정 · 금전\n상세는 블로그에서",
            "sub": "요약 카드 · 본문은 링크",
        },
        {
            "title": "더 보기",
            "body": "전체 운세 읽기",
            "sub": "unseinsight.blogspot.com",
        },
    ]
