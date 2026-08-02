"""Render a mini preview card for every character pack."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from social.card_renderer import render_animal_card, sample_lines_animals
from social.split_character_packs import activate_pack

ROOT = Path(__file__).resolve().parent.parent
CHAR = ROOT / "docs" / "brand" / "characters"
OUT = ROOT / "docs" / "social" / "pack-previews"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    opts = sorted((CHAR / "options").iterdir())
    active_before = "option-01-candy"
    active_file = CHAR / "active_pack.json"
    if active_file.exists():
        active_before = json.loads(active_file.read_text(encoding="utf-8")).get(
            "active", active_before
        )

    d = date.today()
    lines = sample_lines_animals()
    for opt in opts:
        if not opt.is_dir():
            continue
        pack_id = opt.name
        try:
            activate_pack(pack_id)
        except Exception as e:
            print("skip", pack_id, e)
            continue
        out = OUT / f"{pack_id}.png"
        render_animal_card(d, lines, out_path=out)
        # also copy sheet thumbs
        sheet = opt / "sheets" / "animals-sheet.jpg"
        if sheet.exists():
            shutil.copy2(sheet, OUT / f"{pack_id}-sheet.jpg")
        print("preview", out)

    activate_pack(active_before)
    print("restored active", active_before)


if __name__ == "__main__":
    main()
