"""HTML shell for fortune posts (CSS cards + CTA + disclaimer)."""

from __future__ import annotations

from render.affiliate import render_affiliate_block
from render.cta import render_cta


def render_post_html(
    *,
    title: str,
    body_html: str,
    labels: list[str],
    app_name: str,
    app_url: str,
    image_url: str | None = None,
    coupang_url: str = "",
    coupang_title: str = "",
    coupang_description: str = "",
    coupang_banner_url: str = "",
) -> str:
    hero = ""
    if image_url:
        safe_title = (
            title.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        hero = f'<img src="{image_url}" class="f-hero" alt="{safe_title}" />'

    cta = render_cta(app_name, app_url)
    affiliate = render_affiliate_block(
        url=coupang_url,
        title=coupang_title,
        description=coupang_description,
        banner_image_url=coupang_banner_url,
    )
    tags_str = ", ".join(labels)

    return f"""
<div class="f-progress-wrap"><div class="f-progress" id="fProgress"></div></div>
<style>
  html {{ scroll-behavior: smooth; }}
  .f-progress-wrap {{
    position: fixed; top: 0; left: 0; width: 100%; height: 4px;
    background: transparent; z-index: 99999;
  }}
  .f-progress {{
    height: 100%; width: 0%; background: linear-gradient(90deg, #7c3aed, #db2777);
    transition: width 0.1s ease-out;
  }}
  .f-wrap {{
    font-family: 'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
    color: #1f2937; line-height: 1.8; max-width: 820px; margin: 0 auto;
    word-break: keep-all; padding: 8px 4px 40px;
  }}
  .f-hero {{
    width: 100%; border-radius: 14px; margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); display: block;
  }}
  .f-summary {{
    background: linear-gradient(135deg, #f5f3ff 0%, #fdf2f8 100%);
    border: 1px solid #e9d5ff; border-radius: 12px; padding: 18px 20px; margin-bottom: 28px;
  }}
  .f-summary p {{ margin: 0; color: #4c1d95; }}
  .f-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px; margin: 24px 0 32px;
  }}
  .f-card {{
    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 16px 16px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  .f-card h3 {{
    margin: 0 0 8px; font-size: 1.05em; color: #6d28d9; font-weight: 800;
  }}
  .f-card p {{ margin: 0; font-size: 0.95em; color: #374151; }}
  .f-lucky {{
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px;
    padding: 16px 20px; margin: 20px 0 28px;
  }}
  .f-lucky p {{ margin: 6px 0; }}
  .f-avoid {{
    background: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px;
    padding: 16px 20px; margin: 20px 0 28px;
  }}
  .f-highlight {{
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
    padding: 16px 20px; margin: 20px 0 28px;
  }}
  .f-timeline {{ margin: 24px 0 8px; }}
  .f-tip h2, .f-faq h2, .f-wrap h2, .f-avoid h2, .f-highlight h2, .f-timeline h2 {{
    font-size: 1.35em; font-weight: 800; color: #111827;
    border-bottom: 2px solid #c4b5fd; padding-bottom: 10px;
    margin-top: 40px; margin-bottom: 16px;
  }}
  .f-wrap h3 {{ font-size: 1.1em; font-weight: 700; color: #374151; margin-top: 24px; }}
  .f-zodiac-list {{ display: grid; gap: 12px; margin: 20px 0 28px; }}
  .f-z-card {{
    background: #fafafa; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 14px 16px; border-left: 4px solid #8b5cf6;
  }}
  .f-z-card h3 {{ margin: 0 0 6px; color: #5b21b6; font-size: 1.08em; }}
  .f-keyword {{ margin: 0 0 8px; font-weight: 700; color: #db2777; font-size: 0.92em; }}
  .f-z-card p {{ margin: 0; color: #4b5563; font-size: 0.95em; }}
  .f-cta {{
    background: linear-gradient(135deg, #4c1d95 0%, #9d174d 100%);
    color: #fdf4ff; border-radius: 14px; padding: 22px 20px; margin: 40px 0 18px;
    text-align: center;
  }}
  .f-cta-soon {{ background: linear-gradient(135deg, #312e81 0%, #581c87 100%); }}
  .f-cta-title {{ margin: 0 0 8px; font-size: 1.1em; }}
  .f-cta-desc {{ margin: 0 0 12px; opacity: 0.92; font-size: 0.95em; }}
  .f-cta-action a {{
    display: inline-block; background: #fff; color: #6d28d9; font-weight: 800;
    text-decoration: none; padding: 10px 18px; border-radius: 999px;
  }}
  .f-disclaimer {{
    background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239;
    border-radius: 10px; padding: 14px 16px; font-size: 0.85em; margin-bottom: 22px;
  }}
  .f-footer {{
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
    border-top: 1px solid #e5e7eb; padding-top: 16px; font-size: 0.9em; color: #6b7280;
  }}
  .f-tags {{ color: #7c3aed; font-weight: 600; }}
  .f-wrap ul {{ padding-left: 1.2em; }}
  .f-wrap li {{ margin-bottom: 6px; }}
  .f-wrap p {{ margin: 0 0 12px; }}
  .f-affiliate {{
    margin: 36px 0 20px; padding: 20px 18px; border-radius: 14px;
    border: 1px solid #e9d5ff; background: #faf5ff; text-align: center;
  }}
  .f-aff-label {{
    margin: 0 0 8px; font-size: 0.8em; font-weight: 800; letter-spacing: 0.04em;
    color: #7c3aed; text-transform: uppercase;
  }}
  .f-aff-title {{ margin: 0 0 8px; font-size: 1.12em; font-weight: 800; color: #1f2937; }}
  .f-aff-desc {{ margin: 0 0 14px; font-size: 0.95em; color: #4b5563; }}
  .f-aff-banner {{ margin: 0 0 14px; }}
  .f-aff-banner img {{
    max-width: 100%; height: auto; border-radius: 10px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
  }}
  .f-aff-action a {{
    display: inline-block; background: #7c3aed; color: #fff; font-weight: 800;
    text-decoration: none; padding: 11px 18px; border-radius: 999px;
  }}
  .f-aff-legal {{
    margin: 14px 0 0; font-size: 0.78em; color: #6b7280; line-height: 1.5;
  }}
</style>

<div class="f-wrap">
  {hero}
  {body_html}
  {cta}
  {affiliate}
  <div class="f-disclaimer">
    <strong>안내:</strong> 본 콘텐츠는 오락·참고 목적의 운세 정보이며, 의사결정·투자·의료·법률 판단의 근거로 사용하지 마세요.
    중요한 선택은 전문가 상담과 본인의 판단을 우선하세요.
  </div>
  <div class="f-footer">
    <div class="f-tags">Tags: {tags_str}</div>
    <div>매일 아침 업데이트 · 운세 인사이트</div>
  </div>
</div>
<script>
  window.addEventListener('scroll', function () {{
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = height > 0 ? (winScroll / height) * 100 : 0;
    var bar = document.getElementById('fProgress');
    if (bar) bar.style.width = scrolled + '%';
  }});
</script>
"""
