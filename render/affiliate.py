"""Coupang Partners blocks (mid-body + footer) and body injection."""

from __future__ import annotations

import re
from datetime import date

from content.coupang_rotation import COUPANG_DISCLOSURE

# Mid vs footer use different copy pools so the two blocks never feel copy-pasted.
# Index by post date for light day-to-day variety within each pool.

MID_COPY = [
    {
        "label": "잠깐 둘러보기",
        "title": "영역별 운세 보기 전, 가볍게 살펴볼 아이템",
        "desc": "타로 입문 세트·기록용 다이어리 등, 관심 있을 때만 눌러보세요.",
        "cta": "관심 상품 살펴보기 →",
    },
    {
        "label": "루틴 소품",
        "title": "오늘 흐름 정리할 때 곁들이기 좋은 소품",
        "desc": "향초·플래너·감성 문구류 위주로 골라 보셔도 좋습니다.",
        "cta": "관련 상품 보러가기 →",
    },
    {
        "label": "추천 링크",
        "title": "운세 읽을 때 자주 찾는 아이템 모음",
        "desc": "사주·별자리 관련 도서나 카드류가 필요하면 여기서 확인해 보세요.",
        "cta": "상품 리스트 열기 →",
    },
    {
        "label": "참고용",
        "title": "오늘의 키워드에 맞춰 골라보는 소소한 아이템",
        "desc": "필수는 아니에요. 필요한 분만 천천히 둘러보시면 됩니다.",
        "cta": "쿠팡에서 확인하기 →",
    },
]

FOOTER_COPY = [
    {
        "label": "글 마무리 추천",
        "title": "오늘 글을 읽은 뒤 보면 좋은 상품",
        "desc": "아침 루틴·기록·집중을 돕는 아이템을 파트너스 링크로 안내합니다.",
        "cta": "마무리면 추천 보기 →",
    },
    {
        "label": "파트너스",
        "title": "하루를 정리하는 데 도움이 될 수 있는 선택지",
        "desc": "다이어리·수면·집중 용품 등 생활 밀착 상품을 모아 두었습니다.",
        "cta": "추천 목록 보러가기 →",
    },
    {
        "label": "함께 보면",
        "title": "운세 인사이트 독자분들이 자주 찾는 카테고리",
        "desc": "타로·도서·문구 중심으로 연결해 두었습니다. 구매는 선택입니다.",
        "cta": "카테고리 보러가기 →",
    },
    {
        "label": "쇼핑 안내",
        "title": "필요할 때만 쓰는 파트너스 링크",
        "desc": "광고 수익은 콘텐츠 운영에 쓰입니다. 관심 상품이 있을 때만 이용해 주세요.",
        "cta": "링크 열기 →",
    },
]


def _pick_copy(pool: list[dict[str, str]], post_date: date | None, salt: int = 0) -> dict[str, str]:
    if not pool:
        return {"label": "", "title": "", "desc": "", "cta": "보러가기 →"}
    if post_date is None:
        idx = salt % len(pool)
    else:
        idx = (post_date.toordinal() + salt) % len(pool)
    return pool[idx]


def render_affiliate_mid(url: str, post_date: date | None = None) -> str:
    """Compact mid-article partners block (before 영역별 운세). No legal text here."""
    link = (url or "").strip()
    if not link:
        return ""
    copy = _pick_copy(MID_COPY, post_date, salt=0)
    return f"""
      <div class="f-affiliate f-affiliate-mid">
        <p class="f-aff-label">{_esc(copy["label"])}</p>
        <p class="f-aff-title">{_esc(copy["title"])}</p>
        <p class="f-aff-desc">{_esc(copy["desc"])}</p>
        <p class="f-aff-action">
          <a href="{_esc(link)}" rel="sponsored noopener noreferrer" target="_blank">
            {_esc(copy["cta"])}
          </a>
        </p>
      </div>
"""


def render_affiliate_block(
    *,
    url: str,
    title: str = "",
    description: str = "",
    banner_image_url: str = "",
    post_date: date | None = None,
    cta_label: str = "",
    section_label: str = "",
) -> str:
    """End-of-post Coupang block + required disclosure (once, at the bottom)."""
    link = (url or "").strip()
    if not link:
        return f"""
      <div class="f-affiliate f-affiliate-legal-only">
        <p class="f-aff-legal">{_esc(COUPANG_DISCLOSURE)}</p>
      </div>
"""

    copy = _pick_copy(FOOTER_COPY, post_date, salt=3)
    headline = (title or copy["title"]).strip()
    desc = (description or copy["desc"]).strip()
    label = (section_label or copy["label"]).strip()
    button = (cta_label or copy["cta"]).strip()
    banner = (banner_image_url or "").strip()

    img_html = ""
    if banner:
        img_html = f"""
        <p class="f-aff-banner">
          <a href="{_esc(link)}" rel="sponsored noopener noreferrer" target="_blank">
            <img src="{_esc(banner)}" alt="{_esc(headline)}" loading="lazy" />
          </a>
        </p>
"""

    return f"""
      <div class="f-affiliate">
        <p class="f-aff-label">{_esc(label)}</p>
        <p class="f-aff-title">{_esc(headline)}</p>
        <p class="f-aff-desc">{_esc(desc)}</p>
        {img_html}
        <p class="f-aff-action">
          <a href="{_esc(link)}" rel="sponsored noopener noreferrer" target="_blank">
            {_esc(button)}
          </a>
        </p>
        <p class="f-aff-legal">{_esc(COUPANG_DISCLOSURE)}</p>
      </div>
"""


def inject_mid_affiliate(body_html: str, mid_block: str) -> str:
    """Insert mid affiliate block just before 영역별 운세 section when possible."""
    if not mid_block or not body_html:
        return body_html

    patterns = [
        r'(<section[^>]*class="[^"]*f-areas[^"]*"[^>]*>)',
        r'(<h2[^>]*>\s*영역별\s*운세\s*</h2>)',
    ]
    for pat in patterns:
        m = re.search(pat, body_html, flags=re.IGNORECASE)
        if m:
            idx = m.start(1)
            return body_html[:idx] + mid_block + "\n" + body_html[idx:]

    m2 = re.search(
        r"(</section>\s*)(?=<section)",
        body_html,
        flags=re.IGNORECASE,
    )
    if m2:
        idx = m2.end(1)
        return body_html[:idx] + mid_block + "\n" + body_html[idx:]

    cut = max(len(body_html) // 2, 1)
    return body_html[:cut] + mid_block + body_html[cut:]


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
