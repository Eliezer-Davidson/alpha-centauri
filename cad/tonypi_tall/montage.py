#!/usr/bin/env python3
"""Stack the per-part before/after renders into one review sheet.

    edu/.cadenv/bin/python cad/tonypi_tall/montage.py

Reads edu/print_files_tall/renders/*_before.png / *_after.png pairs and
writes edu/print_files_tall/renders/review_sheet.png — one row per part,
BEFORE on the left, AFTER on the right, so the whole variant is reviewable
in a single image (the visual-proof law: claims ship with a picture).
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RENDERS = os.path.join(REPO, "edu/print_files_tall/renders")
OUT = os.path.join(RENDERS, "review_sheet.png")
BG = (20, 17, 14)
FG = (232, 226, 217)
ACCENT = (224, 145, 63)


def load_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    afters = sorted(glob.glob(os.path.join(RENDERS, "*_after.png")))
    rows = []
    for after in afters:
        base = os.path.basename(after)[: -len("_after.png")]
        before = os.path.join(RENDERS, f"{base}_before.png")
        rows.append((base, before if os.path.exists(before) else None, after))
    if not rows:
        raise SystemExit("no *_after.png renders found")

    width = 1500
    label_h = 34
    font = load_font(20)
    imgs, total_h = [], 0
    for base, before, after in rows:
        pair = []
        for path in (before, after):
            if path is None:
                pair.append(None)
                continue
            im = Image.open(path).convert("RGB")
            w = width // 2 - 10
            im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
            pair.append(im)
        h = max(im.height for im in pair if im) + label_h
        imgs.append((base, pair, h))
        total_h += h + 8

    sheet = Image.new("RGB", (width, total_h + 60), BG)
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), "TonyPi TALL variant — before (left) / after (right)",
           fill=ACCENT, font=load_font(24))
    y = 60
    for base, pair, h in imgs:
        d.text((16, y + 4), base, fill=FG, font=font)
        for i, im in enumerate(pair):
            if im is None:
                d.text((16 + i * width // 2, y + h // 2),
                       "(new part — no stock counterpart)", fill=FG, font=font)
                continue
            sheet.paste(im, (i * width // 2 + 5, y + label_h))
        y += h + 8
    sheet.save(OUT)
    print(f"wrote {OUT}  ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
