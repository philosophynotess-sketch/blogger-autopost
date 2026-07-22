"""Blogger API publish helpers."""

from __future__ import annotations

from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config.settings import Settings


def get_blogger_service(settings: Settings):
    if not settings.g_refresh_token or not settings.blogger_blog_id:
        raise RuntimeError("Blogger 인증 정보가 없습니다.")
    creds = Credentials(
        None,
        refresh_token=settings.g_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.g_client_id,
        client_secret=settings.g_client_secret,
        scopes=["https://www.googleapis.com/auth/blogger"],
    )
    return build("blogger", "v3", credentials=creds, cache_discovery=False)


def publish_post(
    settings: Settings,
    *,
    title: str,
    content: str,
    labels: list[str],
    is_draft: bool = False,
) -> dict[str, Any]:
    service = get_blogger_service(settings)
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": labels,
    }
    result = (
        service.posts()
        .insert(blogId=settings.blogger_blog_id, body=body, isDraft=is_draft)
        .execute()
    )
    print(f"✅ Blogger 발행 완료: {result.get('url', title)}")
    return result
