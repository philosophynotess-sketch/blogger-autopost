"""Generate sample social cards for manual upload testing."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from social.card_renderer import (
    render_animal_card,
    render_star_card,
    sample_lines_animals,
    sample_lines_stars,
)

OUT = Path(__file__).resolve().parent.parent / "docs" / "social" / "samples"


def main() -> None:
    d = date.today()
    OUT.mkdir(parents=True, exist_ok=True)
    a = OUT / f"{d.isoformat()}-animals.png"
    s = OUT / f"{d.isoformat()}-stars.png"
    render_animal_card(d, sample_lines_animals(), out_path=a)
    render_star_card(d, sample_lines_stars(), out_path=s)
    print(a)
    print(s)


if __name__ == "__main__":
    main()
