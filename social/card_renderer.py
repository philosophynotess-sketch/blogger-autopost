"""ForceTeller-style dense grid cards with Unse Insight branding."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from social.characters import iter_animals, iter_stars

ROOT = Path(__file__).resolve().parent.parent
MARK_PATH = ROOT / "docs" / "brand" / "logo-mark.png"
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = "C:/Windows/Fonts/malgun.ttf"

# Brand
DEEP = (76, 29, 149)
VIOLET = (124, 58, 237)
PINK = (219, 39, 119)
INK = (31, 41, 55)
MUTED = (107, 114, 128)
BG = (255, 255, 255)
SOFT = (250, 245, 255)
LINE = (237, 233, 254)

# Instagram portrait card (good for feed + story crop)
DEFAULT_SIZE = (1080, 1350)


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    text = (text or "").strip()
    if not text:
        return [""]
    lines: list[str] = []
    cur = ""
    for ch in text:
        trial = cur + ch
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines[:3]  # max 3 lines per cell


def _load_icon(path: Path, size: int) -> Image.Image:
    if path.exists():
        im = Image.open(path).convert("RGBA")
        return im.resize((size, size), Image.Resampling.LANCZOS)
    # fallback pastel circle
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, size - 3, size - 3], fill=(233, 213, 255, 255))
    return im


def render_grid_card(
    *,
    title: str,
    items: list[tuple[str, str, Path]],  # key, label, icon
    lines: list[str],
    subtitle: str = "",
    footer: str = "자세한 운세는 블로그에서 · unseinsight.blogspot.com",
    size: tuple[int, int] = DEFAULT_SIZE,
    out_path: Path | None = None,
) -> Image.Image:
    """
    2-column x 6-row dense fortune card (12 items).
    lines[i] is the one-line advice for items[i].
    """
    w, h = size
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    # header band
    d.rectangle([0, 0, w, 150], fill=SOFT)
    title_font = _font(FONT_BD, 54)
    sub_font = _font(FONT_REG, 24)
    body_font = _font(FONT_REG, 22)
    label_font = _font(FONT_BD, 26)
    footer_font = _font(FONT_REG, 22)

    # title centered
    tw = d.textlength(title, font=title_font)
    d.text(((w - tw) / 2, 36), title, font=title_font, fill=DEEP)
    if subtitle:
        sw = d.textlength(subtitle, font=sub_font)
        d.text(((w - sw) / 2, 100), subtitle, font=sub_font, fill=VIOLET)

    # grid geometry
    top = 170
    bottom = h - 110
    grid_h = bottom - top
    cols, rows = 2, 6
    cell_w = w // cols
    cell_h = grid_h // rows
    icon_size = 72
    left_pad = 28

    for i, (key, label, icon_path) in enumerate(items[:12]):
        r = i // cols
        c = i % cols
        x0 = c * cell_w
        y0 = top + r * cell_h

        # subtle divider
        if r > 0:
            d.line([(40, y0), (w - 40, y0)], fill=LINE, width=1)

        # Benchmark-like: icon left, label + advice stacked to the right
        icon = _load_icon(icon_path, icon_size)
        ix = x0 + left_pad
        iy = y0 + max(8, (cell_h - icon_size) // 2 - 6)
        img.paste(icon, (ix, iy), icon)

        text_x = ix + icon_size + 16
        text_max_w = cell_w - (text_x - x0) - 22

        d.text((text_x, iy + 2), label, font=label_font, fill=DEEP)

        advice = lines[i] if i < len(lines) else ""
        wrapped = _wrap(d, advice, body_font, int(text_max_w))
        ty = iy + 36
        for line in wrapped:
            d.text((text_x, ty), line, font=body_font, fill=INK)
            ty += 26

    # footer bar
    d.rectangle([0, h - 100, w, h], fill=SOFT)
    # logo mark
    if MARK_PATH.exists():
        mark = Image.open(MARK_PATH).convert("RGBA").resize((56, 56), Image.Resampling.LANCZOS)
        img.paste(mark, (36, h - 78), mark)
        footer_x = 108
    else:
        footer_x = 40
    d.text((footer_x, h - 78), "운세 인사이트", font=_font(FONT_BD, 24), fill=DEEP)
    d.rounded_rectangle([footer_x, h - 48, footer_x + 48, h - 42], radius=3, fill=PINK)
    d.text((footer_x, h - 36), footer, font=footer_font, fill=MUTED)

    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, "PNG", optimize=True)
    return img


def render_animal_card(
    post_date: date,
    lines: list[str],
    *,
    out_path: Path | None = None,
) -> Image.Image:
    title = f"{post_date.month:02d}월 {post_date.day:02d}일 띠별 운세"
    items = [(k, lab, p) for k, lab, p in iter_animals()]
    return render_grid_card(
        title=title,
        items=items,
        lines=lines,
        subtitle="한 줄 요약 · 상세는 블로그에서",
        out_path=out_path,
    )


def render_star_card(
    post_date: date,
    lines: list[str],
    *,
    out_path: Path | None = None,
) -> Image.Image:
    title = f"{post_date.month:02d}월 {post_date.day:02d}일 별자리 운세"
    items = [(k, lab, p) for k, lab, p in iter_stars()]
    return render_grid_card(
        title=title,
        items=items,
        lines=lines,
        subtitle="한 줄 요약 · 상세는 블로그에서",
        out_path=out_path,
    )


def sample_lines_animals() -> list[str]:
    return [
        "서두르기보다 정리부터, 페이스가 남는 날",
        "말수 줄이고 듣기, 오해가 풀리는 타이밍",
        "도전은 좋지만 체력 배분이 핵심",
        "가까운 사람과 짧은 대화가 도움이 됨",
        "계획 수정은 OK, 완전 포기는 NO",
        "소비는 한 번 더 생각하고",
        "움직임이 좋은 날, 가벼운 산책 추천",
        "감정보다 일정표가 힘이 됨",
        "아이디어는 메모로 남기면 득",
        "집중 구간을 오전으로 당겨보기",
        "부탁은 구체적으로, 기대는 현실적으로",
        "마무리를 서두르지 말 것",
    ]


def sample_lines_stars() -> list[str]:
    return [
        "추진력 UP, 다만 세부 체크 필수",
        "안정이 운, 루틴을 지키면 이득",
        "정보 교환이 행운을 부름",
        "집에서 충전, 무리한 일정은 조정",
        "자신감은 살리되 독단은 줄이기",
        "정리가 힘이 되는 날, 목록부터",
        "균형 잡힌 선택이 답을 줌",
        "집중력이 좋은 오후를 활용",
        "배움·이동이 흐름을 바꿈",
        "목표를 작게 쪼개면 진행됨",
        "사람 연결과 아이디어가 반짝",
        "감성 충전 후 결정해도 늦지 않음",
    ]


def render_daily_carousel(
    post_date: date,
    slides: list[dict[str, str]],
    *,
    out_dir: Path,
    size: tuple[int, int] = (1080, 1080),
) -> list[str]:
    """Simple 1~3 square slides for daily/SEO posts. Returns saved filenames."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = size
    names: list[str] = []
    title_font = _font(FONT_BD, 56)
    body_font = _font(FONT_BD, 42)
    sub_font = _font(FONT_REG, 28)

    for i, slide in enumerate(slides[:5], start=1):
        img = Image.new("RGB", (w, h), SOFT)
        d = ImageDraw.Draw(img)
        # soft frame
        d.rounded_rectangle([48, 48, w - 48, h - 48], radius=36, fill=BG)
        title = slide.get("title", "")
        body = slide.get("body", "")
        sub = slide.get("sub", "")

        ty = 180
        for line in title.split("\n"):
            tw = d.textlength(line, font=title_font)
            d.text(((w - tw) / 2, ty), line, font=title_font, fill=DEEP)
            ty += 70
        ty += 30
        for line in body.split("\n"):
            bw = d.textlength(line, font=body_font)
            d.text(((w - bw) / 2, ty), line, font=body_font, fill=VIOLET)
            ty += 58
        ty += 24
        for line in sub.split("\n"):
            sw = d.textlength(line, font=sub_font)
            d.text(((w - sw) / 2, ty), line, font=sub_font, fill=MUTED)
            ty += 40

        if MARK_PATH.exists():
            mark = Image.open(MARK_PATH).convert("RGBA").resize((72, 72), Image.Resampling.LANCZOS)
            img.paste(mark, ((w - 72) // 2, h - 160), mark)
        d.text(
            ((w - d.textlength("운세 인사이트", font=sub_font)) / 2, h - 80),
            "운세 인사이트",
            font=sub_font,
            fill=DEEP,
        )

        name = f"carousel-{i:02d}.png"
        img.save(out_dir / name, "PNG", optimize=True)
        names.append(name)
    return names
