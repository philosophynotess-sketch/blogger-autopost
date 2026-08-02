"""Zodiac character asset paths (animals + star signs)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAR_ROOT = ROOT / "docs" / "brand" / "characters"

# Display order matches blog generators
ANIMAL_KEYS = [
    "rat",
    "ox",
    "tiger",
    "rabbit",
    "dragon",
    "snake",
    "horse",
    "sheep",
    "monkey",
    "rooster",
    "dog",
    "pig",
]
ANIMAL_LABELS = [
    "쥐띠",
    "소띠",
    "호랑이띠",
    "토끼띠",
    "용띠",
    "뱀띠",
    "말띠",
    "양띠",
    "원숭이띠",
    "닭띠",
    "개띠",
    "돼지띠",
]

STAR_KEYS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]
STAR_LABELS = [
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


def animal_icon_path(key: str) -> Path:
    return CHAR_ROOT / "animals" / f"{key}.png"


def star_icon_path(key: str) -> Path:
    return CHAR_ROOT / "stars" / f"{key}.png"


def iter_animals() -> list[tuple[str, str, Path]]:
    return [
        (k, ANIMAL_LABELS[i], animal_icon_path(k))
        for i, k in enumerate(ANIMAL_KEYS)
    ]


def iter_stars() -> list[tuple[str, str, Path]]:
    return [
        (k, STAR_LABELS[i], star_icon_path(k))
        for i, k in enumerate(STAR_KEYS)
    ]
