"""Fortune blog daily autopost orchestrator."""

from __future__ import annotations

import sys
import traceback

from config.settings import load_settings
from content.coupang_rotation import pick_coupang_link, pick_coupang_pair
from content.generators import generate_post
from content.schedule import resolve_slot
from publish.blogger import publish_post
from publish.images import generate_and_upload_image
from publish.meta_publish import try_publish_social_folder
from render.affiliate import inject_mid_affiliate, render_affiliate_mid
from render.templates import render_post_html
from social.pipeline import generate_social_assets


def run() -> int:
    settings = load_settings()
    slot = resolve_slot(force_category=settings.force_category)

    print("=" * 56)
    print(f"📅 날짜: {slot.date_ko} ({slot.date_iso})")
    print(f"📂 카테고리: {slot.label} ({slot.category_id})")
    print(f"🖼  이미지: {'필요(SEO)' if slot.needs_image else 'CSS only'}")
    print(f"🧪 DRY_RUN: {settings.dry_run}")
    print("=" * 56)

    post = generate_post(settings, slot)

    labels: list[str] = []
    for tag in [slot.label, *post.tags]:
        if tag and tag not in labels:
            labels.append(tag)
    labels = labels[:5]

    image_url = None
    if slot.needs_image:
        image_url = generate_and_upload_image(settings, post.image_prompt)

    # Two partners slots: mid (before 영역별 운세) + footer. Different URLs when possible.
    # Optional COUPANG_PARTNERS_URL forces both slots to the same override URL.
    if settings.coupang_partners_url:
        mid_url = footer_url = settings.coupang_partners_url
    else:
        mid_url, footer_url = pick_coupang_pair(slot.post_date)

    body_with_mid = inject_mid_affiliate(
        post.body_html,
        render_affiliate_mid(mid_url, post_date=slot.post_date),
    )

    html = render_post_html(
        title=post.title,
        body_html=body_with_mid,
        labels=labels,
        app_name=settings.app_name,
        app_url=settings.app_url,
        image_url=image_url,
        coupang_url=footer_url,
        coupang_title=settings.coupang_title,
        coupang_description=settings.coupang_description,
        coupang_banner_url=settings.coupang_banner_url,
        post_date=slot.post_date,
    )

    print(f"📰 제목: {post.title}")
    print(f"🏷  라벨: {labels}")
    if post.seo_topic:
        print(f"🔎 SEO 주제: {post.seo_topic}")
    print(f"📝 본문 길이: {len(body_with_mid)} chars")
    print(f"🛒 쿠팡 중간: {mid_url}")
    print(f"🛒 쿠팡 하단: {footer_url}")

    # SNS cards + captions (app deep-link later; blog URL for now)
    social_dir = None
    try:
        social_dir = generate_social_assets(
            settings, slot, post.body_html, blog_url="https://unseinsight.blogspot.com/"
        )
        try_publish_social_folder(social_dir)
    except Exception as e:
        print(f"⚠️ 소셜 에셋 단계 오류(블로그 발행은 계속): {e}")

    if settings.dry_run:
        print("🧪 DRY_RUN=1 — Blogger 발행 생략")
        preview = post.body_html[:400].replace("\n", " ")
        print(f"미리보기: {preview}...")
        return 0

    publish_post(
        settings,
        title=post.title,
        content=html,
        labels=labels,
        is_draft=False,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
