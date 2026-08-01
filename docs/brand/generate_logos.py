"""Generate 운세 인사이트 brand logo assets into docs/brand/."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent

VIOLET = (124, 58, 237)
DEEP = (76, 29, 149)
PINK = (219, 39, 119)
INK = (31, 41, 55)
CREAM = (250, 245, 255)
WHITE = (255, 255, 255)

FONT_REG = "C:/Windows/Fonts/malgun.ttf"
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"


def load(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def rounded_rect(draw: ImageDraw.ImageDraw, xy, r, fill) -> None:
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def draw_moon_mark(
    d: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: float,
    fill_bg: tuple,
    cream: tuple = CREAM + (255,),
) -> None:
    """Crescent + spark mark centered at cx, cy."""
    s = scale
    d.ellipse(
        [cx - int(80 * s), cy - int(100 * s), cx + int(70 * s), cy + int(100 * s)],
        fill=cream,
    )
    d.ellipse(
        [cx - int(30 * s), cy - int(110 * s), cx + int(110 * s), cy + int(90 * s)],
        fill=fill_bg,
    )
    sparks = [
        (cx + int(75 * s), cy - int(55 * s), int(14 * s)),
        (cx + int(100 * s), cy - int(15 * s), int(9 * s)),
        (cx + int(72 * s), cy + int(25 * s), int(7 * s)),
    ]
    for ox, oy, rad in sparks:
        d.ellipse([ox - rad, oy - rad, ox + rad, oy + rad], fill=WHITE + (245,))


def gradient_circle(
    d: ImageDraw.ImageDraw, icon_x: int, icon_y: int, icon_size: int
) -> tuple[int, int, int]:
    last = VIOLET
    for i in range(icon_size // 2, 0, -1):
        t = i / (icon_size / 2)
        r = int(DEEP[0] * (1 - t) + VIOLET[0] * t)
        g = int(DEEP[1] * (1 - t) + VIOLET[1] * t)
        b = int(DEEP[2] * (1 - t) + VIOLET[2] * t)
        last = (r, g, b)
        d.ellipse(
            [
                icon_x + icon_size // 2 - i,
                icon_y + icon_size // 2 - i,
                icon_x + icon_size // 2 + i,
                icon_y + icon_size // 2 + i,
            ],
            fill=(r, g, b, 255),
        )
    return last


def make_primary_horizontal() -> Path:
    w, h = 1600, 480
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    icon_size = 280
    icon_x, icon_y = 60, (h - icon_size) // 2
    fill = gradient_circle(d, icon_x, icon_y, icon_size)
    cx = icon_x + icon_size // 2
    cy = icon_y + icon_size // 2
    draw_moon_mark(d, cx, cy, 0.7, fill + (255,))

    title_font = load(FONT_BD, 96)
    sub_font = load(FONT_REG, 36)
    tag_font = load(FONT_REG, 26)
    title = "운세 인사이트"
    tx = icon_x + icon_size + 48
    ty = h // 2 - 70
    d.text((tx, ty), title, font=title_font, fill=DEEP + (255,))
    bbox = d.textbbox((tx, ty), title, font=title_font)
    d.rounded_rectangle(
        [tx, bbox[3] + 12, tx + 160, bbox[3] + 20], radius=4, fill=PINK + (255,)
    )
    d.text((tx, bbox[3] + 36), "UNSE INSIGHT", font=sub_font, fill=VIOLET + (255,))
    d.text(
        (tx, bbox[3] + 90),
        "하루를 읽는 운세 정보 미디어",
        font=tag_font,
        fill=INK + (200,),
    )

    path = OUT / "logo-primary.png"
    img.save(path, "PNG")
    return path


def make_primary_dark() -> Path:
    w, h = 1600, 480
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rounded_rect(d, [20, 20, w - 20, h - 20], 40, DEEP + (255,))

    icon_size = 240
    icon_x, icon_y = 80, (h - icon_size) // 2
    d.ellipse(
        [icon_x, icon_y, icon_x + icon_size, icon_y + icon_size],
        fill=VIOLET + (255,),
    )
    cx = icon_x + icon_size // 2
    cy = icon_y + icon_size // 2
    draw_moon_mark(d, cx, cy, 0.6, VIOLET + (255,))

    title_font = load(FONT_BD, 92)
    sub_font = load(FONT_REG, 34)
    tx = icon_x + icon_size + 48
    ty = h // 2 - 60
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


def make_stacked() -> Path:
    w, h = 1000, 1100
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    icon_size = 420
    icon_x = (w - icon_size) // 2
    icon_y = 80
    fill = gradient_circle(d, icon_x, icon_y, icon_size)
    cx = icon_x + icon_size // 2
    cy = icon_y + icon_size // 2
    draw_moon_mark(d, cx, cy, 1.0, fill + (255,))

    title_font = load(FONT_BD, 88)
    sub_font = load(FONT_REG, 34)
    title = "운세 인사이트"
    bbox = d.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) // 2
    ty = icon_y + icon_size + 48
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

    path = OUT / "logo-stacked.png"
    img.save(path, "PNG")
    return path


def make_mark_only() -> Path:
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 48
    last = VIOLET
    for i in range((size - 2 * pad) // 2, 0, -1):
        t = i / ((size - 2 * pad) / 2)
        r = int(DEEP[0] * (1 - t) + VIOLET[0] * t)
        g = int(DEEP[1] * (1 - t) + VIOLET[1] * t)
        b = int(DEEP[2] * (1 - t) + VIOLET[2] * t)
        last = (r, g, b)
        cx = cy = size // 2
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(r, g, b, 255))
    cx = cy = size // 2
    draw_moon_mark(d, cx, cy, 2.0, last + (255,))

    path = OUT / "logo-mark.png"
    img.save(path, "PNG")
    for s, name in [
        (512, "logo-mark-512.png"),
        (192, "logo-mark-192.png"),
        (64, "favicon-64.png"),
    ]:
        img.resize((s, s), Image.Resampling.LANCZOS).save(OUT / name, "PNG")
    return path


def make_social_avatar() -> Path:
    size = 1080
    img = Image.new("RGBA", (size, size), DEEP + (255,))
    d = ImageDraw.Draw(img)
    # outer ring only in upper area; solid field below for clean type
    d.ellipse([90, 40, size - 90, size - 200], outline=VIOLET + (255,), width=28)
    d.ellipse([130, 80, size - 130, size - 240], fill=DEEP + (255,))
    # fill remaining bottom so type sits on solid brand color
    d.rectangle([0, size - 260, size, size], fill=DEEP + (255,))
    cx, cy = size // 2, size // 2 - 90
    draw_moon_mark(d, cx, cy, 1.45, DEEP + (255,))

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


def main() -> None:
    paths = [
        make_primary_horizontal(),
        make_primary_dark(),
        make_stacked(),
        make_mark_only(),
        make_social_avatar(),
    ]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
