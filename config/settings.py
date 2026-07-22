"""Runtime settings and category catalog for fortune blog autopost."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# Category IDs used by schedule + generators
CAT_DAILY = "daily_overview"
CAT_ANIMALS = "zodiac_animals"
CAT_STARS = "star_signs"
CAT_SEO = "seo_deep"

CATEGORY_LABELS: dict[str, str] = {
    CAT_DAILY: "오늘의 운세",
    CAT_ANIMALS: "띠별 운세",
    CAT_STARS: "별자리 운세",
    CAT_SEO: "운세 가이드",
}

# weekday: Mon=0 ... Sun=6 (datetime.weekday)
WEEKDAY_ROTATION: dict[int, str] = {
    0: CAT_DAILY,
    1: CAT_ANIMALS,
    2: CAT_STARS,
    3: CAT_DAILY,
    4: CAT_ANIMALS,
    5: CAT_STARS,
    6: CAT_SEO,
}

ZODIAC_ANIMALS = [
    "쥐",
    "소",
    "호랑이",
    "토끼",
    "용",
    "뱀",
    "말",
    "양",
    "원숭이",
    "닭",
    "개",
    "돼지",
]

STAR_SIGNS = [
    "양자리",
    "황소자리",
    "쌍둥이자리",
    "게자리",
    "사자자리",
    "처녀자리",
    "천칭자리",
    "전갈자리",
    "사수자리",
    "염소자리",
    "물병자리",
    "물고기자리",
]


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    g_client_id: str
    g_client_secret: str
    g_refresh_token: str
    blogger_blog_id: str
    app_name: str = "운세 앱"
    app_url: str = ""
    hf_token: str = ""
    imgbb_api_key: str = ""
    dry_run: bool = False
    force_category: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"

    @property
    def gemini_url(self) -> str:
        return (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        )


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"필수 환경변수가 없습니다: {name}")
    return value


def load_settings() -> Settings:
    dry = os.environ.get("DRY_RUN", "").strip() in ("1", "true", "True", "yes")
    force = os.environ.get("FORCE_CATEGORY", "").strip() or None
    if force and force not in CATEGORY_LABELS:
        raise RuntimeError(
            f"FORCE_CATEGORY 값이 올바르지 않습니다: {force}. "
            f"허용: {', '.join(CATEGORY_LABELS)}"
        )

    # dry-run still needs gemini unless we later mock; require keys for real pipeline
    if dry and not os.environ.get("GEMINI_API_KEY"):
        # allow schedule-only smoke without keys when SKIP_GENERATE=1
        pass

    gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini and not dry:
        raise RuntimeError("필수 환경변수가 없습니다: GEMINI_API_KEY")

    if dry and not gemini:
        # placeholder so Settings can load for pure unit paths
        gemini = "dry-run-placeholder"

    def optional_blogger() -> tuple[str, str, str, str]:
        if dry and not os.environ.get("BLOGGER_BLOG_ID"):
            return ("", "", "", "")
        return (
            _require("G_CLIENT_ID"),
            _require("G_CLIENT_SECRET"),
            _require("G_REFRESH_TOKEN"),
            _require("BLOGGER_BLOG_ID"),
        )

    cid, csec, rtok, blog_id = optional_blogger()

    return Settings(
        gemini_api_key=gemini,
        g_client_id=cid,
        g_client_secret=csec,
        g_refresh_token=rtok,
        blogger_blog_id=blog_id,
        app_name=os.environ.get("APP_NAME", "운세 앱").strip() or "운세 앱",
        app_url=os.environ.get("APP_URL", "").strip(),
        hf_token=os.environ.get("HF_TOKEN", "").strip(),
        imgbb_api_key=os.environ.get("IMGBB_API_KEY", "").strip(),
        dry_run=dry,
        force_category=force,
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
        or "gemini-2.5-flash",
    )
