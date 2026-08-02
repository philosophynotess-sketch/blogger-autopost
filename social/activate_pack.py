"""Activate a character pack: python -m social.activate_pack option-01-candy"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from social.split_character_packs import activate_pack

CHAR = Path(__file__).resolve().parent.parent / "docs" / "brand" / "characters"


def list_packs() -> None:
    opts = CHAR / "options"
    if not opts.exists():
        print("no packs")
        return
    for p in sorted(opts.iterdir()):
        meta = p / "meta.json"
        if meta.exists():
            data = json.loads(meta.read_text(encoding="utf-8"))
            print(f"{data.get('id')}: {data.get('title')} — {data.get('desc')}")
        else:
            print(p.name)


def main() -> None:
    if len(sys.argv) < 2:
        list_packs()
        print("\nusage: python -m social.activate_pack option-01-candy")
        print("       python -m social.activate_pack --list")
        return
    if sys.argv[1] in ("-l", "--list"):
        list_packs()
        return
    activate_pack(sys.argv[1])


if __name__ == "__main__":
    main()
