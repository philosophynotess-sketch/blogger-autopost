"""Coupang Partners blocks (mid-body + footer) and body injection."""

from __future__ import annotations

import re

from content.coupang_rotation import COUPANG_DISCLOSURE


def render_affiliate_mid(url: str) -> str:
    """Compact mid-article partners block (before 영역별 운세)."""
    link = (url or "").strip()
    if not link:
        return ""
    return f"""
      <div class="f-affiliate f-affiliate-mid">
        <p class="f-aff-label">파트너스 추천</p>
        <p class="f-aff-title">영역별 운세 보기 전, 가볍게 살펴보기 좋은 아이템</p>
        <p class="f-aff-desc">타로·다이어리·루틴 소품 등 관심 상품을 확인해 보세요.</p>
        <p class="f-aff-action">
          <a href="{_esc(link)}" rel="sponsored noopener noreferrer" target="_blank">
            추천 상품 보러가기 →
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
) -> str:
    """Return HTML for end-of-post Coupang block + required disclosure."""
    link = (url or "").strip()
    if not link:
        return f"""
      <div class="f-affiliate f-affiliate-legal-only">
        <p class="f-aff-legal">{_esc(COUPANG_DISCLOSURE)}</p>
      </div>
"""

    headline = (title or "오늘의 운세 루틴에 어울리는 아이템").strip()
    desc = (
        description
        or "타로·다이어리·감성 소품 등, 아침 루틴에 가볍게 곁들이기 좋은 상품을 모았습니다."
    ).strip()
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
        <p class="f-aff-label">파트너스 추천</p>
        <p class="f-aff-title">{_esc(headline)}</p>
        <p class="f-aff-desc">{_esc(desc)}</p>
        {img_html}
        <p class="f-aff-action">
          <a href="{_esc(link)}" rel="sponsored noopener noreferrer" target="_blank">
            추천 상품 보러가기 →
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

    # Fallback: after 시간대별 흐름 section if present
    m2 = re.search(
        r'(</section>\s*)(?=<section)',
        body_html,
        flags=re.IGNORECASE,
    )
    if m2:
        # prefer first section close after timeline-ish content
        # insert after first </section>
        idx = m2.end(1)
        return body_html[:idx] + mid_block + "\n" + body_html[idx:]

    # Last resort: upper-middle of body
    cut = max(len(body_html) // 2, 1)
    return body_html[:cut] + mid_block + body_html[cut:]


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
