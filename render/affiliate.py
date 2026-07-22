"""Coupang Partners (or generic affiliate) footer block."""

from __future__ import annotations


def render_affiliate_block(
    *,
    url: str,
    title: str = "",
    description: str = "",
    banner_image_url: str = "",
) -> str:
    """Return HTML for end-of-post affiliate block. Empty if no URL."""
    link = (url or "").strip()
    if not link:
        return ""

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
        <p class="f-aff-legal">
          이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
        </p>
      </div>
"""


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
