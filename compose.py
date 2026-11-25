#!/usr/bin/env python3
"""Compose a 1600x1600 newspaper front page (entry.png) from panels/p1..p6."""

import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1600
PANELS_DIR = "panels"
OUT = "entry.png"

BLACK = (10, 10, 10)
WHITE = (245, 245, 245)
RED = (178, 24, 24)
PAPER = (238, 234, 226)

FONT_CANDIDATES = {
    "serif_bold": [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf",
    ],
    "condensed": [
        "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ],
    "bold": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "black": [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
}


def pick(kind):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No font found for {kind}")


def font(kind, size):
    return ImageFont.truetype(pick(kind), size)


def fit_text(draw, text, kind, max_size, max_width):
    """Return a font whose rendered text width fits max_width."""
    size = max_size
    while size > 8:
        f = font(kind, size)
        w = draw.textlength(text, font=f)
        if w <= max_width:
            return f
        size -= 2
    return font(kind, 8)


def cover_crop(img, cw, ch):
    """Resize + center-crop image so it exactly fills cw x ch."""
    scale = max(cw / img.width, ch / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - cw) // 2
    top = (nh - ch) // 2
    return img.crop((left, top, left + cw, top + ch))


HEADLINES = [
    "SHENZHOU-24: PAKISTAN'S FIRST ASTRONAUT LAUNCHES",
    "HOSTAGE SIEGE GRIPS CARTAGENA",
    "RECORD KING TIDES FLOOD BAY AREA",
    "XI PURGE: POLITBURO STAR PROBED",
    "HUAWEI CONVICTED IN U.S. COURT",
    "IOWA TOWN EVACUATES FOR AZIDE BLAST",
]


def main():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    # ---- Masthead ----
    masthead_h = 240
    draw.rectangle([0, 0, W, masthead_h], fill=BLACK)
    mast_text = "THE WORLD"
    mast_font = fit_text(draw, mast_text, "serif_bold", 170, W - 160)
    bbox = draw.textbbox((0, 0), mast_text, font=mast_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((W - tw) / 2 - bbox[0], (masthead_h - th) / 2 - bbox[1]),
              mast_text, font=mast_font, fill=WHITE)

    # ---- Red dateline strip ----
    strip_top = masthead_h
    strip_h = 78
    draw.rectangle([0, strip_top, W, strip_top + strip_h], fill=RED)
    strip_text = "TUESDAY, 24 NOVEMBER 2026 — THE DAY IN WORLD NEWS"
    strip_font = fit_text(draw, strip_text, "condensed", 46, W - 120)
    bbox = draw.textbbox((0, 0), strip_text, font=strip_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((W - tw) / 2 - bbox[0], strip_top + (strip_h - th) / 2 - bbox[1]),
              strip_text, font=strip_font, fill=WHITE)

    # ---- Grid ----
    margin = 24
    gap = 24
    grid_top = strip_top + strip_h + margin
    grid_bottom = H - margin
    cell_w = (W - 2 * margin - 2 * gap) // 3
    cell_h = (grid_bottom - grid_top - gap) // 2
    bar_h = 110

    for idx in range(6):
        row, col = divmod(idx, 3)
        x0 = margin + col * (cell_w + gap)
        y0 = grid_top + row * (cell_h + gap)
        img_h = cell_h - bar_h

        panel = Image.open(os.path.join(PANELS_DIR, f"p{idx + 1}.png")).convert("RGB")
        panel = cover_crop(panel, cell_w, img_h)
        page.paste(panel, (x0, y0))

        # caption bar
        bar_top = y0 + img_h
        draw.rectangle([x0, bar_top, x0 + cell_w, bar_top + bar_h], fill=BLACK)

        # red number chip
        chip = 56
        cx = x0 + 22
        cy = bar_top + (bar_h - chip) // 2
        draw.rectangle([cx, cy, cx + chip, cy + chip], fill=RED)
        num_font = font("black", 34)
        nbbox = draw.textbbox((0, 0), str(idx + 1), font=num_font)
        nw, nh = nbbox[2] - nbbox[0], nbbox[3] - nbbox[1]
        draw.text((cx + (chip - nw) / 2 - nbbox[0], cy + (chip - nh) / 2 - nbbox[1]),
                  str(idx + 1), font=num_font, fill=WHITE)

        # headline text, fitted to remaining width, wrapped to 2 lines if needed
        text_x = cx + chip + 22
        avail_w = x0 + cell_w - 22 - text_x
        fpath = pick("bold")
        size = 34
        while size > 14:
            f = ImageFont.truetype(fpath, size)
            if draw.textlength(HEADLINES[idx], font=f) <= avail_w:
                break
            size -= 1
        hl_font = ImageFont.truetype(fpath, size)
        if draw.textlength(HEADLINES[idx], font=hl_font) > avail_w:
            # wrap into two balanced lines
            words = HEADLINES[idx].split()
            best, best_diff = None, None
            for k in range(1, len(words)):
                l1, l2 = " ".join(words[:k]), " ".join(words[k:])
                w1 = draw.textlength(l1, font=hl_font)
                w2 = draw.textlength(l2, font=hl_font)
                if w1 <= avail_w and w2 <= avail_w:
                    diff = abs(w1 - w2)
                    if best_diff is None or diff < best_diff:
                        best, best_diff = (l1, l2), diff
            lines = best if best else (HEADLINES[idx], "")
        else:
            lines = (HEADLINES[idx],)
        bbox = draw.textbbox((0, 0), "AX", font=hl_font)
        line_h = (bbox[3] - bbox[1]) + 8
        total_h = line_h * len([l for l in lines if l])
        ty = bar_top + (bar_h - total_h) / 2 - bbox[1]
        for line in lines:
            if not line:
                continue
            draw.text((text_x, ty), line, font=hl_font, fill=WHITE)
            ty += line_h

    page.save(OUT)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
