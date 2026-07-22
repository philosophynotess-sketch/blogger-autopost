"""App promotion CTA block (URL optional while app is in development)."""

from __future__ import annotations


def render_cta(app_name: str, app_url: str) -> str:
    name = (app_name or "운세 인사이트").strip()
    url = (app_url or "").strip()

    if url:
        return f"""
      <div class="f-cta">
        <p class="f-cta-title">더 자세한 오늘의 운세는 <strong>{_esc(name)}</strong>에서</p>
        <p class="f-cta-desc">띠·별자리·테마 운세를 한곳에서 확인해 보세요.</p>
        <p class="f-cta-action">
          <a href="{_esc(url)}" rel="noopener noreferrer" target="_blank">{_esc(name)} 바로가기 →</a>
        </p>
      </div>
"""

    return f"""
      <div class="f-cta f-cta-soon">
        <p class="f-cta-title"><strong>{_esc(name)}</strong> 준비 중</p>
      </div>
"""


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
