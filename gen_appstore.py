#!/usr/bin/env python3
"""
Malaysia Pocket — 6.9" App Store screenshot generator.

Canvas is 1320 x 2868 (iPhone 17/16 Pro Max portrait), the current App Store
Connect requirement for the 6.9" display size group. Output is flat RGB PNG with
no alpha, which is what App Store Connect accepts.

The marketing design follows the app's own design system rather than inventing a
second one: flat colour fields, no gradients, no drop shadows, SF Pro throughout.
Deep indigo is the canvas — the app icon and the default theme are both indigo as
of 3.0 — `accent` marks the eyebrow, and `urgent` red is used on exactly one
frame, the emergency one, because in this app red means "call for help" and
nothing else.

The captures in real-screenshots-v3/ are taken with the ad slots suppressed. An
App Store screenshot showing a third-party banner sells the banner, not the app,
and Apple treats an ad in a screenshot as misrepresenting the experience.

Usage:  python3 gen_appstore.py
Input:  real-screenshots-v2/*.png   (raw 1320x2868 simulator captures)
Output: appstore-6.9/*.png
"""

from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "real-screenshots-v3")
OUT = os.path.join(HERE, "appstore-6.9")

W, H = 1320, 2868

# ── Palette (from Malaysia Law 101/Extension/AppTheme.swift) ────────────────
CANVAS      = (26, 32, 74)       # deep indigo — darker sibling of the icon gradient
CANVAS_RED  = (74, 22, 22)       # deep red field, emergency frame only
ACCENT      = (143, 160, 245)    # PocketTheme.indigo, dark variant #8FA0F5
URGENT      = (255, 122, 107)    # AppTheme.urgent, dark variant #FF7A6B
HEADLINE    = (242, 245, 244)    # AppTheme.background, light #F2F5F4
SUBLINE     = (170, 178, 214)    # muted ink on the indigo field
BEZEL       = (52, 62, 120)

# ── Layout ─────────────────────────────────────────────────────────────────
MARGIN      = 96
EYEBROW_Y   = 190
HEAD_Y      = 268
PHONE_W     = 1008              # device width on canvas
PHONE_GAP   = 150               # copy block to device; the device then bleeds
CORNER      = 74                # off the bottom edge

FONT_DIR = "/Library/Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_EYEBROW = lambda: font("SF-Pro-Display-Semibold.otf", 40)
F_HEAD    = lambda: font("SF-Pro-Display-Bold.otf", 104)
F_SUB     = lambda: font("SF-Pro-Display-Regular.otf", 44)


def draw_text_block(draw, lines, y, fnt, fill, leading):
    """Left-aligned block; returns the y below the last line."""
    for line in lines:
        draw.text((MARGIN, y), line, font=fnt, fill=fill)
        y += leading
    return y


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], []
    for w in words:
        trial = " ".join(cur + [w])
        if draw.textlength(trial, font=fnt) <= max_w:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def rounded_device(src_path, width, corner):
    """Scale a raw capture to `width` and round its corners, on transparency."""
    shot = Image.open(src_path).convert("RGB")
    height = round(shot.height * width / shot.width)
    shot = shot.resize((width, height), Image.LANCZOS)

    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, height - 1],
                                           radius=corner, fill=255)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out.paste(shot, (0, 0), mask)
    return out


def make(src_name, out_name, eyebrow, headline, subline, emergency=False):
    src_path = os.path.join(SRC, src_name)
    if not os.path.exists(src_path):
        print(f"  SKIP (missing) {src_path}")
        return

    canvas = Image.new("RGBA", (W, H), CANVAS_RED + (255,) if emergency
                       else CANVAS + (255,))
    draw = ImageDraw.Draw(canvas)
    tint = URGENT if emergency else ACCENT

    # Eyebrow — uppercase, letterspaced by hand (PIL has no tracking).
    f_eye = F_EYEBROW()
    x = MARGIN
    for ch in eyebrow.upper():
        draw.text((x, EYEBROW_Y), ch, font=f_eye, fill=tint)
        x += draw.textlength(ch, font=f_eye) + 5

    # Headline
    f_head = F_HEAD()
    head_lines = headline.split("\n")
    y = draw_text_block(draw, head_lines, HEAD_Y, f_head, HEADLINE, 122)

    # Subline
    f_sub = F_SUB()
    sub_lines = wrap(draw, subline, f_sub, W - MARGIN * 2)
    y = draw_text_block(draw, sub_lines, y + 28, f_sub, SUBLINE, 60)

    # Device — sits a fixed gap under the copy, so a one-line subline does not
    # leave a hole and a three-line one does not crowd the frame.
    phone_top = y + PHONE_GAP
    phone = rounded_device(src_path, PHONE_W, CORNER)
    px = (W - PHONE_W) // 2
    # Hairline bezel so a light screenshot does not float on the dark field.
    ImageDraw.Draw(canvas).rounded_rectangle(
        [px - 5, phone_top - 5, px + PHONE_W + 4, H + 40],
        radius=CORNER + 5, outline=BEZEL, width=5)
    canvas.paste(phone, (px, phone_top), phone)

    os.makedirs(OUT, exist_ok=True)
    canvas.convert("RGB").save(os.path.join(OUT, out_name), "PNG")
    print(f"  {out_name}")


FRAMES = [
    dict(src_name="01_home.png", out_name="01_home.png",
         eyebrow="Malaysia Pocket",
         headline="Know what to do\nin the next hour",
         subline="Emergency numbers, your rights and every complaint "
                 "channel — in one place."),
    dict(src_name="02_situations.png", out_name="02_situations.png",
         eyebrow="Start here",
         headline="Start with what\nhappened to you",
         subline="25 situations in plain language — not “which Act does "
                 "this fall under”."),
    dict(src_name="03_deadline.png", out_name="03_deadline.png",
         eyebrow="Deadlines",
         headline="Miss the date,\nlose the case",
         subline="60 days for unfair dismissal. Track every step, and get "
                 "reminded at 30, 7 and 1 day."),
    # The letter itself renders below the fold on a single capture, so the frame shows
    # the form that writes it and the copy says so — promising a document the image does
    # not contain is the kind of screenshot Apple rejects and users resent.
    dict(src_name="04_letter.png", out_name="04_letter.png",
         eyebrow="Complaint letters",
         headline="Your details once,\nthe letter writes itself",
         subline="A formal surat aduan in Bahasa Malaysia, built as you type. "
                 "Nothing leaves your phone."),
    dict(src_name="05_rights.png", out_name="05_rights.png",
         eyebrow="Know your rights",
         headline="Police stops. Work.\nTenancy. Scams.",
         subline="28 topics that say what the law actually gives you, and "
                 "what it costs you."),
    dict(src_name="06_emergency.png", out_name="06_emergency.png",
         eyebrow="Get help now",
         headline="999, 994,\n997, 991",
         subline="One tap to the right line, always on the home screen. "
                 "No account, works offline.",
         emergency=True),
]


if __name__ == "__main__":
    print(f"Writing 6.9\" App Store screenshots ({W}x{H}) to appstore-6.9/")
    for frame in FRAMES:
        make(**frame)
    print("done")
