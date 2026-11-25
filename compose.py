import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 2000
MASTHEAD_H = 130
STRIP_H = 55
HERO_H = 430
FOOTER_H = 50
COL_W = W // 2
STORIES_TOP = MASTHEAD_H + STRIP_H + HERO_H
STORIES_H = H - FOOTER_H - STORIES_TOP
ROWS = 14
ROW_H = STORIES_H / ROWS
CAPTION_BAR_H = 46

RED = (201, 18, 33)
WHITE = (255, 255, 255)
OFFWHITE = (230, 230, 230)
BLACK = (0, 0, 0)
PAGE_BG = (16, 16, 16)
ROW_A = (25, 25, 25)
ROW_B = (35, 35, 35)
DIVIDER = (62, 62, 62)

REGION_COLORS = {
    "ASIA": (14, 118, 99),
    "MIDEAST": (176, 133, 60),
    "EUROPE": (139, 95, 168),
    "LATAM": (178, 91, 58),
    "US": (70, 98, 143),
    "TECH": (95, 122, 52),
    "SCIENCE": (61, 155, 181),
    "CULTURE": (168, 74, 110),
}

STORIES = [
    ("ASIA", "Shenzhou-24 carries Pakistan's first astronaut to orbit"),
    ("ASIA", "Xi purge widens: politburo star under investigation"),
    ("ASIA", "Solomon Islands signs security treaty with Australia"),
    ("ASIA", "North Korea expels Swiss diplomat over sanctions"),
    ("MIDEAST", "Houthis take second swipe at Riyadh's tallest tower"),
    ("MIDEAST", "Ukraine's Mediterranean strike becomes a problem for Meloni"),
    ("EUROPE", "Russia's own figures show almost 500,000 war deaths"),
    ("LATAM", "Armed men take hostages in Cartagena tourist district"),
    ("US", "CIA and ODNI suffer cybersecurity breach, source says"),
    ("US", "Record king tides leave Bay Area roads flooded"),
    ("US", "Iowa town evacuates as Army detonates lead azide stockpile"),
    ("US", "Six killed as plane crashes off Mississippi coast"),
    ("US", "Fort Hood shooter Nidal Hasan petitions to delay execution"),
    ("US", "House counsel refused to join raid on Rep. Ilhan Omar"),
    ("US", "Kilmar Abrego Garcia leaves US for Spain, ending deportation battle"),
    ("US", "Trump plays the hits at Thanksgiving turkey pardon"),
    ("TECH", "GTA VI's jaw-dropping success in figures"),
    ("TECH", "CoD and Fortnite engagement plunges after GTA VI launch"),
    ("TECH", "Apple Mail gains four new features in iOS 27"),
    ("TECH", "Black Friday laptop deals land early"),
    ("SCIENCE", "Claude and ChatGPT's new biology skills wow scientists"),
    ("CULTURE", "Dancing With the Stars names historic season 35 winner"),
    ("CULTURE", "Thanksgiving storm threatens Macy's parade"),
    ("CULTURE", "Blade Runner 2099 score lands below both originals"),
    ("CULTURE", "Pope Francis' diary excerpts reveal spiritual struggles"),
    ("US", "Stock futures slip as traders await key inflation report"),
    ("ASIA", "Asian stocks slide as AI trade doubts resurface"),
    ("CULTURE", "Hunger Games prequel eyes Thanksgiving box office"),
]

BASE = os.path.dirname(os.path.abspath(__file__))

FONT_PATHS = {
    "serif": [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/GeorgiaBold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    ],
    "sans": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "cond": [
        "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Narrow.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ],
}

_used_fonts = {}
_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _cache:
        f = None
        for path in FONT_PATHS[kind]:
            if os.path.exists(path):
                try:
                    f = ImageFont.truetype(path, size)
                    _used_fonts[kind] = path
                    break
                except OSError:
                    continue
        if f is None:
            f = ImageFont.load_default()
        _cache[key] = f
    return _cache[key]


def crop_to_fill(path, box_w, box_h):
    img = Image.open(path).convert("RGB")
    scale = max(box_w / img.width, box_h / img.height)
    rw = max(box_w, round(img.width * scale))
    rh = max(box_h, round(img.height * scale))
    img = img.resize((rw, rh), Image.LANCZOS)
    left = (rw - box_w) // 2
    top = (rh - box_h) // 2
    return img.crop((left, top, left + box_w, top + box_h))


def draw_chip(d, x, cy, label, fill, text_fill, f, pad_x=8, h=20, radius=4):
    tw = d.textlength(label, font=f)
    w = tw + pad_x * 2
    d.rounded_rectangle([x, cy - h / 2, x + w, cy + h / 2], radius=radius, fill=fill)
    d.text((x + w / 2, cy + 1), label, font=f, fill=text_fill, anchor="mm")
    return w


def wrap_truncate(d, text, f, max_w, max_lines=2):
    lines = []
    cur = ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if not cur or d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and " " in last and d.textlength(last + "\u2026", font=f) > max_w:
        last = last.rsplit(" ", 1)[0]
    out[-1] = last + "\u2026"
    return out


def main():
    img = Image.new("RGB", (W, H), PAGE_BG)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, MASTHEAD_H], fill=BLACK)
    d.text(
        (W / 2, MASTHEAD_H / 2 + 4),
        "THE WORLD",
        font=font("serif", 96),
        fill=WHITE,
        anchor="mm",
    )

    strip_top = MASTHEAD_H
    d.rectangle([0, strip_top, W, strip_top + STRIP_H], fill=RED)
    d.text(
        (28, strip_top + STRIP_H / 2),
        "TUESDAY, 24 NOVEMBER 2026 \u2014 30 STORIES, 8 REGIONS",
        font=font("cond", 27),
        fill=WHITE,
        anchor="lm",
    )

    hero_top = strip_top + STRIP_H
    heroes = [
        (
            os.path.join(BASE, "panels", "p1.png"),
            "01",
            "SHENZHOU-24: PAKISTAN'S FIRST ASTRONAUT LAUNCHES",
        ),
        (
            os.path.join(BASE, "panels", "p5.png"),
            "02",
            "HUAWEI CONVICTED IN U.S. COURT",
        ),
    ]
    for i, (path, chip_label, caption) in enumerate(heroes):
        x0 = i * COL_W
        try:
            panel = crop_to_fill(path, COL_W, HERO_H)
        except Exception:
            panel = Image.new("RGB", (COL_W, HERO_H), (42, 42, 42))
            pd = ImageDraw.Draw(panel)
            pd.text(
                (COL_W / 2, HERO_H / 2),
                "MISSING PANEL",
                font=font("sans", 24),
                fill=(130, 130, 130),
                anchor="mm",
            )
        img.paste(panel, (x0, hero_top))
        bar_y = hero_top + HERO_H - CAPTION_BAR_H
        d.rectangle([x0, bar_y, x0 + COL_W, hero_top + HERO_H], fill=BLACK)
        cy = bar_y + CAPTION_BAR_H / 2
        chip_w = draw_chip(
            d, x0 + 12, cy, chip_label, RED, WHITE, font("sans", 14), pad_x=9, h=24
        )
        size = 18
        while size > 10 and d.textlength(caption, font=font("sans", size)) > COL_W - chip_w - 46:
            size -= 1
        d.text(
            (x0 + 12 + chip_w + 12, cy),
            caption,
            font=font("sans", size),
            fill=WHITE,
            anchor="lm",
        )

    for r in range(ROWS):
        y0 = STORIES_TOP + round(r * ROW_H)
        y1 = STORIES_TOP + round((r + 1) * ROW_H)
        d.rectangle([0, y0, W, y1], fill=ROW_A if r % 2 == 0 else ROW_B)
        d.line([0, y1, W, y1], fill=DIVIDER, width=1)
    d.line([COL_W, STORIES_TOP, COL_W, STORIES_TOP + STORIES_H], fill=DIVIDER, width=1)

    num_f = font("sans", 19)
    chip_f = font("sans", 12)
    head_f = font("serif", 22)
    head_x_off = 62
    max_head_w = COL_W - head_x_off - 16
    for idx, (region, headline) in enumerate(STORIES):
        col = idx // ROWS
        r = idx % ROWS
        x0 = col * COL_W
        y0 = STORIES_TOP + round(r * ROW_H)
        d.text((x0 + 16, y0 + 23), f"{idx + 3:02d}", font=num_f, fill=RED, anchor="lm")
        draw_chip(d, x0 + head_x_off, y0 + 23, region, REGION_COLORS[region], WHITE, chip_f, h=19)
        ly = y0 + 41
        for line in wrap_truncate(d, headline, head_f, max_head_w, 2):
            d.text((x0 + head_x_off, ly), line, font=head_f, fill=WHITE, anchor="la")
            ly += 26

    foot_top = H - FOOTER_H
    d.rectangle([0, foot_top, W, H], fill=BLACK)
    d.line([0, foot_top, W, foot_top], fill=RED, width=2)
    foot_f = font("sans", 16)
    d.text(
        (28, foot_top + FOOTER_H / 2),
        "THE WORLD \u2014 the day in one page",
        font=foot_f,
        fill=OFFWHITE,
        anchor="lm",
    )
    d.text(
        (W - 28, foot_top + FOOTER_H / 2),
        "24 NOV 2026",
        font=foot_f,
        fill=OFFWHITE,
        anchor="rm",
    )

    out = os.path.join(BASE, "entry.png")
    img.save(out)
    print(f"saved {out} ({img.width}x{img.height})")
    for kind, path in _used_fonts.items():
        print(f"font[{kind}] = {path}")


if __name__ == "__main__":
    main()
