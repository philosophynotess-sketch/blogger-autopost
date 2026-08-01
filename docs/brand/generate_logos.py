"""Generate 운세 인사이트 brand assets using the preferred AI mark as the official symbol."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
AI_MARK = OUT / "logo-mark-ai-concept.jpg"

VIOLET = (124, 58, 237)
DEEP = (76, 29, 149)
PINK = (219, 39, 119)
INK = (31, 41, 55)
WHITE = (255, 255, 255)
SOFT = (250, 245, 255)

FONT_REG = "C:/Windows/Fonts/malgun.ttf"
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"


def load(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def rounded_rect(draw: ImageDraw.ImageDraw, xy, r, fill) -> None:
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def load_ai_mark() -> Image.Image:
    if not AI_MARK.exists():
        raise FileNotFoundError(f"Missing preferred mark: {AI_MARK}")
    return Image.open(AI_MARK).convert("RGBA")


def fit_mark(mark: Image.Image, size: int) -> Image.Image:
    return mark.resize((size, size), Image.Resampling.LANCZOS)


def make_mark_exports(mark: Image.Image) -> list[Path]:
    paths: list[Path] = []
    # Official mark = AI concept at full res
    primary = OUT / "logo-mark.png"
    mark.save(primary, "PNG")
    paths.append(primary)

    for s, name in [
        (512, "logo-mark-512.png"),
        (192, "logo-mark-192.png"),
        (64, "favicon-64.png"),
    ]:
        p = OUT / name
        fit_mark(mark, s).save(p, "PNG")
        paths.append(p)
    return paths


def make_primary_horizontal(mark: Image.Image) -> Path:
    w, h = 1600, 480
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    icon_size = 300
    icon = fit_mark(mark, icon_size)
    icon_x, icon_y = 40, (h - icon_size) // 2
    img.paste(icon, (icon_x, icon_y), icon)

    title_font = load(FONT_BD, 96)
    sub_font = load(FONT_REG, 36)
    tag_font = load(FONT_REG, 26)
    title = "운세 인사이트"
    tx = icon_x + icon_size + 40
    ty = h // 2 - 70
    d.text((tx, ty), title, font=title_font, fill=DEEP + (255,))
    bbox = d.textbbox((tx, ty), title, font=title_font)
    d.rounded_rectangle(
        [tx, bbox[3] + 12, tx + 160, bbox[3] + 20], radius=4, fill=PINK + (255,)
    )
    d.text((tx, bbox[3] + 36), "UNSE INSIGHT", font=sub_font, fill=VIOLET + (255,))
    d.text(
        (tx, bbox[3] + 90),
        "하루를 읽는 운세 정보 미디어 · unseinsight.blogspot.com",
        font=tag_font,
        fill=INK + (200,),
    )

    path = OUT / "logo-primary.png"
    img.save(path, "PNG")
    return path


def make_primary_dark(mark: Image.Image) -> Path:
    w, h = 1600, 480
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded_rect(d, [20, 20, w - 20, h - 20], 40, DEEP + (255,))

    icon_size = 260
    icon = fit_mark(mark, icon_size)
    icon_x, icon_y = 70, (h - icon_size) // 2
    img.paste(icon, (icon_x, icon_y), icon)

    title_font = load(FONT_BD, 92)
    sub_font = load(FONT_REG, 34)
    tx = icon_x + icon_size + 40
    ty = h // 2 - 55
    d.text((tx, ty), "운세 인사이트", font=title_font, fill=WHITE + (255,))
    bbox = d.textbbox((tx, ty), "운세 인사이트", font=title_font)
    d.rounded_rectangle(
        [tx, bbox[3] + 10, tx + 140, bbox[3] + 18], radius=4, fill=PINK + (255,)
    )
    d.text(
        (tx, bbox[3] + 32),
        "UNSE INSIGHT",
        font=sub_font,
        fill=(221, 214, 254, 255),
    )

    path = OUT / "logo-primary-dark.png"
    img.save(path, "PNG")
    return path


def make_stacked(mark: Image.Image) -> Path:
    w, h = 1000, 1200
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    icon_size = 520
    icon = fit_mark(mark, icon_size)
    icon_x = (w - icon_size) // 2
    icon_y = 60
    img.paste(icon, (icon_x, icon_y), icon)

    title_font = load(FONT_BD, 88)
    sub_font = load(FONT_REG, 34)
    title = "운세 인사이트"
    bbox = d.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) // 2
    ty = icon_y + icon_size + 36
    d.text((tx, ty), title, font=title_font, fill=DEEP + (255,))
    bbox2 = d.textbbox((tx, ty), title, font=title_font)
    line_w = 120
    d.rounded_rectangle(
        [(w - line_w) // 2, bbox2[3] + 16, (w + line_w) // 2, bbox2[3] + 24],
        radius=4,
        fill=PINK + (255,),
    )
    sub = "UNSE INSIGHT"
    sb = d.textbbox((0, 0), sub, font=sub_font)
    d.text(
        ((w - (sb[2] - sb[0])) // 2, bbox2[3] + 48),
        sub,
        font=sub_font,
        fill=VIOLET + (255,),
    )
    tag = "unseinsight.blogspot.com"
    tag_font = load(FONT_REG, 28)
    tb = d.textbbox((0, 0), tag, font=tag_font)
    d.text(
        ((w - (tb[2] - tb[0])) // 2, bbox2[3] + 100),
        tag,
        font=tag_font,
        fill=INK + (180,),
    )

    path = OUT / "logo-stacked.png"
    img.save(path, "PNG")
    return path


def make_social_avatar(mark: Image.Image) -> Path:
    size = 1080
    img = Image.new("RGBA", (size, size), DEEP + (255,))
    d = ImageDraw.Draw(img)

    # soft light panel for the mark (matches AI soft UI look)
    panel = 620
    px = (size - panel) // 2
    py = 90
    rounded_rect(d, [px, py, px + panel, py + panel], 96, SOFT + (255,))
    icon = fit_mark(mark, 540)
    img.paste(icon, ((size - 540) // 2, py + 40), icon)

    title_font = load(FONT_BD, 68)
    sub_font = load(FONT_REG, 26)
    title = "운세 인사이트"
    bbox = d.textbbox((0, 0), title, font=title_font)
    d.text(
        ((size - (bbox[2] - bbox[0])) // 2, size - 200),
        title,
        font=title_font,
        fill=WHITE + (255,),
    )
    sub = "unseinsight.blogspot.com"
    sb = d.textbbox((0, 0), sub, font=sub_font)
    d.text(
        ((size - (sb[2] - sb[0])) // 2, size - 110),
        sub,
        font=sub_font,
        fill=(221, 214, 254, 255),
    )

    path = OUT / "logo-avatar-instagram.png"
    img.save(path, "PNG")
    return path


def make_social_avatar_mark_only(mark: Image.Image) -> Path:
    """Clean square avatar: soft mark on deep purple (no text)."""
    size = 1080
    img = Image.new("RGBA", (size, size), DEEP + (255,))
    d = ImageDraw.Draw(img)
    panel = 780
    px = (size - panel) // 2
    py = (size - panel) // 2
    rounded_rect(d, [px, py, px + panel, py + panel], 120, SOFT + (255,))
    icon = fit_mark(mark, 680)
    img.paste(icon, ((size - 680) // 2, (size - 680) // 2), icon)
    path = OUT / "logo-avatar-mark.png"
    img.save(path, "PNG")
    return path


def main() -> None:
    mark = load_ai_mark()
    paths: list[Path] = []
    paths.extend(make_mark_exports(mark))
    paths.append(make_primary_horizontal(mark))
    paths.append(make_primary_dark(mark))
    paths.append(make_stacked(mark))
    paths.append(make_social_avatar(mark))
    paths.append(make_social_avatar_mark_only(mark))
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
