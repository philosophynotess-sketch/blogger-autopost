"""Optional AI thumbnail for SEO deep-dive posts."""

from __future__ import annotations

import base64

import requests

from config.settings import Settings

FALLBACK_IMAGE = (
    "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200"
)


def generate_and_upload_image(settings: Settings, image_prompt: str) -> str | None:
    """Return image URL or None if generation is skipped/failed."""
    prompt = (image_prompt or "").strip() or (
        "soft mystical morning light, calm editorial illustration, no text"
    )
    print("🎨 SEO 썸네일 생성 시도...")

    if not settings.hf_token:
        print("ℹ️ HF_TOKEN 없음 — 폴백 이미지 사용")
        return FALLBACK_IMAGE

    headers = {"Authorization": f"Bearer {settings.hf_token}"}
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    try:
        res = requests.post(
            url,
            headers=headers,
            json={
                "inputs": (
                    f"Editorial soft illustration, {prompt}, "
                    "high quality, no watermark, no text"
                )
            },
            timeout=90,
        )
        if res.status_code != 200:
            print(f"⚠️ 이미지 생성 실패 HTTP {res.status_code}")
            return FALLBACK_IMAGE
        return upload_to_imgbb(settings, res.content) or FALLBACK_IMAGE
    except Exception as e:
        print(f"⚠️ 이미지 생성 예외: {e}")
        return FALLBACK_IMAGE


def upload_to_imgbb(settings: Settings, image_bytes: bytes) -> str | None:
    if not settings.imgbb_api_key:
        print("ℹ️ IMGBB_API_KEY 없음 — 이미지 업로드 스킵")
        return None
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": settings.imgbb_api_key,
            "image": base64.b64encode(image_bytes).decode("utf-8"),
        }
        response = requests.post(url, data=payload, timeout=40)
        response.raise_for_status()
        return response.json()["data"]["url"]
    except Exception as e:
        print(f"⚠️ ImgBB 업로드 실패: {e}")
        return None
