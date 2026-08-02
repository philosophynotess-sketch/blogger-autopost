from datetime import date
from pathlib import Path

from social.card_renderer import render_animal_card, sample_lines_animals


def test_render_animal_card_bytes(tmp_path: Path):
    out = tmp_path / "a.png"
    img = render_animal_card(date(2026, 8, 2), sample_lines_animals(), out_path=out)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert img.size[0] == 1080
