"""Fortune blog daily autopost orchestrator."""

from __future__ import annotations

import sys
import traceback

from config.settings import load_settings
from content.generators import generate_post
from content.schedule import resolve_slot
from publish.blogger import publish_post
from publish.images import generate_and_upload_image
from render.templates import render_post_html


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

    html = render_post_html(
        title=post.title,
        body_html=post.body_html,
        labels=labels,
        app_name=settings.app_name,
        app_url=settings.app_url,
        image_url=image_url,
        coupang_url=settings.coupang_partners_url,
        coupang_title=settings.coupang_title,
        coupang_description=settings.coupang_description,
        coupang_banner_url=settings.coupang_banner_url,
    )

    print(f"📰 제목: {post.title}")
    print(f"🏷  라벨: {labels}")
    if post.seo_topic:
        print(f"🔎 SEO 주제: {post.seo_topic}")
    print(f"📝 본문 길이: {len(post.body_html)} chars")

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
