"""Meta (Facebook Page / Instagram) publish helpers.

Phase 0-1: dry-run by default. Set META_PUBLISH=1 and tokens to attempt live post.
App integration (saas-template) is deferred.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests


GRAPH = "https://graph.facebook.com/v21.0"


def meta_config() -> dict[str, str]:
    return {
        "page_id": os.environ.get("META_PAGE_ID", "").strip(),
        "page_token": os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip(),
        "ig_user_id": os.environ.get("IG_USER_ID", "").strip(),
        "enabled": os.environ.get("META_PUBLISH", "").strip()
        in ("1", "true", "True", "yes"),
    }


def publish_facebook_photo(
    *,
    image_path: Path,
    caption: str,
    page_id: str,
    page_token: str,
) -> dict[str, Any]:
    """Upload local image to Facebook Page as photo post."""
    url = f"{GRAPH}/{page_id}/photos"
    with open(image_path, "rb") as f:
        res = requests.post(
            url,
            data={"caption": caption, "access_token": page_token},
            files={"source": f},
            timeout=120,
        )
    res.raise_for_status()
    return res.json()


def publish_instagram_feed(
    *,
    image_url: str,
    caption: str,
    ig_user_id: str,
    page_token: str,
) -> dict[str, Any]:
    """
    Instagram content publish requires a publicly accessible image URL.
    Local files must be hosted first (Blogger image host, ImgBB, etc.).
    """
    create = f"{GRAPH}/{ig_user_id}/media"
    r1 = requests.post(
        create,
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": page_token,
        },
        timeout=60,
    )
    r1.raise_for_status()
    creation_id = r1.json()["id"]
    publish = f"{GRAPH}/{ig_user_id}/media_publish"
    r2 = requests.post(
        publish,
        data={"creation_id": creation_id, "access_token": page_token},
        timeout=60,
    )
    r2.raise_for_status()
    return r2.json()


def try_publish_social_folder(folder: Path) -> dict[str, Any]:
    """
    If META_PUBLISH=1 and tokens exist, post first feed-*.png to Facebook.
    Instagram needs public URL — logs skip reason until hosted.
    """
    cfg = meta_config()
    result: dict[str, Any] = {"facebook": None, "instagram": None, "skipped": []}
    caption_path = folder / "caption.txt"
    caption = caption_path.read_text(encoding="utf-8") if caption_path.exists() else ""

    images = sorted(folder.glob("feed-*.png")) + sorted(folder.glob("carousel-01.png"))
    if not images:
        result["skipped"].append("no feed image")
        return result

    image = images[0]
    if not cfg["enabled"]:
        result["skipped"].append("META_PUBLISH not enabled (dry)")
        print(f"📵 Meta dry-run — would post {image.name}")
        print(f"   caption preview: {caption[:120].replace(chr(10), ' ')}...")
        return result

    if not cfg["page_id"] or not cfg["page_token"]:
        result["skipped"].append("missing META_PAGE_ID or META_PAGE_ACCESS_TOKEN")
        return result

    try:
        result["facebook"] = publish_facebook_photo(
            image_path=image,
            caption=caption,
            page_id=cfg["page_id"],
            page_token=cfg["page_token"],
        )
        print("✅ Facebook Page 게시:", result["facebook"])
    except Exception as e:
        result["facebook_error"] = str(e)
        print(f"❌ Facebook 게시 실패: {e}")

    if cfg["ig_user_id"]:
        result["skipped"].append(
            "Instagram needs public image_url — host feed image then set IG publish"
        )
    else:
        result["skipped"].append("IG_USER_ID not set")

    (folder / "meta-publish-result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result
