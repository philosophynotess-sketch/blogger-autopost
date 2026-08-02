"""Split generated sprite sheets into character option packs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHAR = ROOT / "docs" / "brand" / "characters"
SESSION = Path(
    r"C:\Users\user\.grok\sessions\C%3A%5CUsers%5Cuser%5Cauto-blog%5Cblogger-autopost"
    r"\019f8a47-8956-7c00-84ad-92bbc4040a67\images"
)

ANIMALS = [
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
STARS = [
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

PACKS = {
    "option-01-candy": {
        "animals": SESSION / "6.jpg",
        "stars": SESSION / "7.jpg",
        "title": "캔디 카와이",
        "desc": "반짝 눈·파스텔 스티커",
    },
    "option-02-clay": {
        "animals": SESSION / "5.jpg",
        "stars": SESSION / "4.jpg",
        "title": "클레이 토이",
        "desc": "말랑 3D 점토 느낌",
    },
    "option-03-minimal": {
        "animals": SESSION / "9.jpg",
        "stars": SESSION / "12.jpg",
        "title": "미니멀 이모지",
        "desc": "심플 플랫 아이콘",
    },
    "option-04-lavender": {
        "animals": SESSION / "8.jpg",
        "stars": SESSION / "10.jpg",
        "title": "라벤더 드림",
        "desc": "운세 브랜드 보라 톤",
    },
    "option-05-comic": {
        "animals": SESSION / "11.jpg",
        "stars": SESSION / "13.jpg",
        "title": "코믹 치비",
        "desc": "액세서리·표정 다양",
    },
}


def split_sheet(path: Path, out_dir: Path, names: list[str], rows: int = 3, cols: int = 4) -> None:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    cw, ch = w // cols, h // rows
    pad = int(min(cw, ch) * 0.05)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(names):
        r, c = i // cols, i % cols
        box = (c * cw + pad, r * ch + pad, (c + 1) * cw - pad, (r + 1) * ch - pad)
        cell = im.crop(box)
        s = max(cell.size)
        canvas = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        canvas.paste(cell, ((s - cell.size[0]) // 2, (s - cell.size[1]) // 2), cell)
        canvas.resize((512, 512), Image.Resampling.LANCZOS).save(out_dir / f"{name}.png")


def archive_classic() -> None:
    opt0 = CHAR / "options" / "option-00-classic"
    (opt0 / "animals").mkdir(parents=True, exist_ok=True)
    (opt0 / "stars").mkdir(parents=True, exist_ok=True)
    (opt0 / "sheets").mkdir(parents=True, exist_ok=True)
    for n in ANIMALS:
        src = CHAR / "animals" / f"{n}.png"
        if src.exists():
            shutil.copy2(src, opt0 / "animals" / f"{n}.png")
    for n in STARS:
        src = CHAR / "stars" / f"{n}.png"
        if src.exists():
            shutil.copy2(src, opt0 / "stars" / f"{n}.png")
    for sheet in ("animals-sheet.jpg", "stars-sheet.jpg"):
        s = CHAR / "sheets" / sheet
        if s.exists():
            shutil.copy2(s, opt0 / "sheets" / sheet)
    (opt0 / "meta.json").write_text(
        json.dumps(
            {
                "id": "option-00-classic",
                "title": "클래식",
                "desc": "첫 생성 세트",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def activate_pack(pack_id: str) -> None:
    active = CHAR / "options" / pack_id
    if not active.exists():
        raise FileNotFoundError(pack_id)
    for kind, names in (("animals", ANIMALS), ("stars", STARS)):
        dest = CHAR / kind
        dest.mkdir(parents=True, exist_ok=True)
        for n in names:
            shutil.copy2(active / kind / f"{n}.png", dest / f"{n}.png")
    # sheets for reference
    sheets = CHAR / "sheets"
    sheets.mkdir(parents=True, exist_ok=True)
    for name in ("animals-sheet.jpg", "stars-sheet.jpg"):
        src = active / "sheets" / name
        if src.exists():
            shutil.copy2(src, sheets / name)
    (CHAR / "active_pack.json").write_text(
        json.dumps({"active": pack_id}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("active ->", pack_id)


def main() -> None:
    archive_classic()
    for pack_id, meta in PACKS.items():
        base = CHAR / "options" / pack_id
        sheets = base / "sheets"
        sheets.mkdir(parents=True, exist_ok=True)
        a_src, s_src = meta["animals"], meta["stars"]
        if not a_src.exists() or not s_src.exists():
            print("MISSING", pack_id, a_src, s_src)
            continue
        a_sheet = sheets / "animals-sheet.jpg"
        s_sheet = sheets / "stars-sheet.jpg"
        shutil.copy2(a_src, a_sheet)
        shutil.copy2(s_src, s_sheet)
        split_sheet(a_sheet, base / "animals", ANIMALS)
        split_sheet(s_sheet, base / "stars", STARS)
        (base / "meta.json").write_text(
            json.dumps(
                {
                    "id": pack_id,
                    "title": meta["title"],
                    "desc": meta["desc"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print("OK", pack_id)
    activate_pack("option-01-candy")


if __name__ == "__main__":
    main()
