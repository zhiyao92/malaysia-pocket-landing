#!/usr/bin/env python3
"""
Generates 6.9-inch App Store marketing screenshots for Malaysia Pocket.
Canvas: 1320 x 2868 px (iPhone 16 Pro Max / 15 Pro Max portrait) — the
current App Store Connect requirement for the 6.9" display size group.

Saved as flat RGB PNG (no alpha channel), per App Store Connect upload
requirements. Drawing itself happens in RGBA so translucent "glass" cards
composite correctly, then the canvas is flattened before writing to disk.
"""

from PIL import Image, ImageDraw, ImageFont, ImageChops
import math, os

OUT = os.path.join(os.path.dirname(__file__), "screenshots")
ICON_PATH = os.path.join(os.path.dirname(__file__), "app-icon.png")
os.makedirs(OUT, exist_ok=True)

W, H = 1320, 2868

# ── Brand colours ─────────────────────────────────────────────────────────
GREEN       = (31, 111, 92)
GREEN_DARK  = (14, 60, 48)
GREEN_LIGHT = (45, 148, 122)
WHITE       = (255, 255, 255, 255)
OFF_WHITE   = (247, 250, 248, 255)
MUTED       = (150, 205, 190, 255)      # muted text on green bg
MUTED_DARK  = (120, 150, 140, 255)      # muted text on white card
CARD_BG     = (255, 255, 255, 255)
CARD_BORDER = (220, 238, 232, 255)
INK         = (24, 48, 42, 255)
URGENT      = (214, 90, 90, 255)
URGENT_BG   = (255, 240, 238, 255)
URGENT_BORDER = (232, 190, 190, 255)
GOLD        = (196, 150, 46, 255)
GOLD_BG     = (255, 250, 235, 255)
GOLD_BORDER = (222, 195, 140, 255)

# ── Fonts ────────────────────────────────────────────────────────────────

def font(size, bold=False):
    candidates_bold = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in (candidates_bold if bold else candidates):
        try:
            return ImageFont.truetype(path, size, index=1 if (bold and path.endswith(".ttc")) else 0)
        except Exception:
            continue
    return ImageFont.load_default()

def text_centered(draw, text, y, fnt, color=WHITE):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, font=fnt, fill=color)
    return bbox[3] - bbox[1]

def wrap_text(draw, text, x, y, max_width, fnt, color, line_spacing=1.32, center=False):
    words = text.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_width:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    for i, l in enumerate(lines):
        ly = y + i * int(fnt.size * line_spacing)
        if center:
            bbox = draw.textbbox((0, 0), l, font=fnt)
            lw = bbox[2] - bbox[0]
            draw.text(((W - lw) // 2, ly), l, font=fnt, fill=color)
        else:
            draw.text((x, ly), l, font=fnt, fill=color)
    return y + len(lines) * int(fnt.size * line_spacing)

# ── Base drawing helpers ─────────────────────────────────────────────────

def gradient_bg(img, top_color, bottom_color):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

def rounded_rect(draw, x0, y0, x1, y1, radius, fill=None, border=None, border_width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                            outline=border, width=border_width)

def blend(bg, fg, alpha):
    """Manually pre-blend fg over bg at alpha (0-1) — used for translucent
    'glass' cards drawn on top of a gradient, since flattening RGBA->RGB at
    save time does not composite; only real per-pixel drawing does."""
    return tuple(int(bg[i] * (1 - alpha) + fg[i] * alpha) for i in range(3)) + (255,)

# ── Vector icon glyphs (no emoji — Helvetica has no colour glyph table) ──

def icon_badge(draw, cx, cy, r, bg, glyph, glyph_color=WHITE):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)
    glyph(draw, cx, cy, r * 0.52, glyph_color)

def g_phone(draw, cx, cy, s, c):
    w, h = s * 0.85, s * 1.55
    ang = math.radians(-28)
    corners = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    pts = [(cx + x*math.cos(ang) - y*math.sin(ang), cy + x*math.sin(ang) + y*math.cos(ang)) for x, y in corners]
    draw.polygon(pts, fill=c)

def g_shield(draw, cx, cy, s, c):
    pts = [(cx, cy-s*1.05), (cx+s*0.85, cy-s*0.55), (cx+s*0.85, cy+s*0.15),
           (cx, cy+s*1.1), (cx-s*0.85, cy+s*0.15), (cx-s*0.85, cy-s*0.55)]
    draw.polygon(pts, fill=c)

def g_bolt(draw, cx, cy, s, c):
    pts = [(cx+s*0.15, cy-s*1.1), (cx-s*0.55, cy+s*0.1), (cx-s*0.05, cy+s*0.1),
           (cx-s*0.15, cy+s*1.1), (cx+s*0.6, cy-s*0.15), (cx+s*0.1, cy-s*0.15)]
    draw.polygon(pts, fill=c)

def g_doc(draw, cx, cy, s, c):
    w = max(3, int(s*0.16))
    draw.rounded_rectangle([cx-s*0.65, cy-s, cx+s*0.65, cy+s], radius=s*0.18, outline=c, width=w)
    for i in range(3):
        y = cy - s*0.35 + i*s*0.4
        draw.line([(cx-s*0.35, y), (cx+s*0.35, y)], fill=c, width=w)

def g_clock(draw, cx, cy, s, c):
    w = max(3, int(s*0.2))
    draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=c, width=w)
    draw.line([(cx, cy), (cx, cy-s*0.55)], fill=c, width=w)
    draw.line([(cx, cy), (cx+s*0.42, cy+s*0.18)], fill=c, width=w)

def g_bell(draw, cx, cy, s, c):
    draw.pieslice([cx-s*0.75, cy-s*0.95, cx+s*0.75, cy+s*0.55], 180, 360, fill=c)
    draw.rectangle([cx-s*0.75, cy-s*0.2, cx+s*0.75, cy+s*0.25], fill=c)
    draw.polygon([(cx-s*0.85, cy+s*0.25), (cx+s*0.85, cy+s*0.25), (cx+s*0.6, cy+s*0.5), (cx-s*0.6, cy+s*0.5)], fill=c)
    draw.ellipse([cx-s*0.2, cy+s*0.45, cx+s*0.2, cy+s*0.75], fill=c)

def g_search(draw, cx, cy, s, c):
    r = s*0.62
    ox, oy = cx - s*0.18, cy - s*0.18
    w = max(3, int(s*0.22))
    draw.ellipse([ox-r, oy-r, ox+r, oy+r], outline=c, width=w)
    hx1, hy1 = ox + r*0.72, oy + r*0.72
    draw.line([(hx1, hy1), (cx+s*0.85, cy+s*0.85)], fill=c, width=w)

def g_warning(draw, cx, cy, s, c, bg):
    pts = [(cx, cy-s*1.05), (cx+s*0.95, cy+s*0.75), (cx-s*0.95, cy+s*0.75)]
    draw.polygon(pts, fill=c)
    w = max(3, int(s*0.2))
    draw.line([(cx, cy-s*0.15), (cx, cy+s*0.28)], fill=bg, width=w)
    draw.ellipse([cx-w*0.6, cy+s*0.42, cx+w*0.6, cy+s*0.42+w*1.2], fill=bg)

def g_crown(draw, cx, cy, s, c):
    pts = [(cx-s, cy+s*0.55), (cx-s, cy-s*0.05), (cx-s*0.5, cy+s*0.25),
           (cx, cy-s*0.65), (cx+s*0.5, cy+s*0.25), (cx+s, cy-s*0.05), (cx+s, cy+s*0.55)]
    draw.polygon(pts, fill=c)
    draw.rectangle([cx-s, cy+s*0.55, cx+s, cy+s*0.75], fill=c)

def g_lock(draw, cx, cy, s, c):
    draw.rounded_rectangle([cx-s*0.7, cy-s*0.05, cx+s*0.7, cy+s], radius=s*0.15, fill=c)
    w = max(3, int(s*0.22))
    draw.arc([cx-s*0.45, cy-s*1.1, cx+s*0.45, cy-s*0.05], start=180, end=360, fill=c, width=w)
    draw.ellipse([cx-s*0.12, cy+s*0.25, cx+s*0.12, cy+s*0.49], fill=CARD_BG)

def g_check(draw, cx, cy, s, c):
    w = max(3, int(s*0.24))
    draw.line([(cx-s*0.7, cy+s*0.05), (cx-s*0.1, cy+s*0.6)], fill=c, width=w)
    draw.line([(cx-s*0.1, cy+s*0.6), (cx+s*0.85, cy-s*0.5)], fill=c, width=w)

def g_flag(draw, cx, cy, s, c):
    w = max(3, int(s*0.16))
    draw.line([(cx-s*0.55, cy-s), (cx-s*0.55, cy+s)], fill=c, width=w)
    draw.polygon([(cx-s*0.55, cy-s), (cx+s*0.85, cy-s*0.5), (cx-s*0.55, cy-s*0.05)], fill=c)

def g_calendar(draw, cx, cy, s, c):
    w = max(3, int(s*0.16))
    draw.rounded_rectangle([cx-s, cy-s*0.75, cx+s, cy+s], radius=s*0.16, outline=c, width=w)
    draw.line([(cx-s, cy-s*0.25), (cx+s, cy-s*0.25)], fill=c, width=w)
    draw.line([(cx-s*0.5, cy-s*1.05), (cx-s*0.5, cy-s*0.5)], fill=c, width=w)
    draw.line([(cx+s*0.5, cy-s*1.05), (cx+s*0.5, cy-s*0.5)], fill=c, width=w)

def g_scale(draw, cx, cy, s, c):
    w = max(3, int(s*0.14))
    draw.line([(cx, cy-s), (cx, cy+s*0.85)], fill=c, width=w)
    draw.line([(cx-s*0.9, cy-s*0.55), (cx+s*0.9, cy-s*0.55)], fill=c, width=w)
    draw.polygon([(cx-s*0.9, cy-s*0.55), (cx-s*1.15, cy+s*0.05), (cx-s*0.65, cy+s*0.05)], outline=c, width=w)
    draw.polygon([(cx+s*0.9, cy-s*0.55), (cx+s*1.15, cy+s*0.05), (cx+s*0.65, cy+s*0.05)], outline=c, width=w)
    draw.rectangle([cx-s*0.55, cy+s*0.85, cx+s*0.55, cy+s*1.0], fill=c)

def g_car(draw, cx, cy, s, c):
    draw.rounded_rectangle([cx-s, cy-s*0.15, cx+s, cy+s*0.35], radius=s*0.2, fill=c)
    draw.polygon([(cx-s*0.55, cy-s*0.15), (cx-s*0.25, cy-s*0.55), (cx+s*0.35, cy-s*0.55), (cx+s*0.6, cy-s*0.15)], fill=c)
    draw.ellipse([cx-s*0.6, cy+s*0.15, cx-s*0.2, cy+s*0.55], fill=c)
    draw.ellipse([cx+s*0.2, cy+s*0.15, cx+s*0.6, cy+s*0.55], fill=c)

def g_share(draw, cx, cy, s, c):
    w = max(3, int(s*0.18))
    draw.line([(cx, cy-s*0.2), (cx, cy+s)], fill=c, width=w)
    draw.line([(cx-s*0.55, cy-s*0.3), (cx, cy-s*0.95)], fill=c, width=w)
    draw.line([(cx+s*0.55, cy-s*0.3), (cx, cy-s*0.95)], fill=c, width=w)
    draw.arc([cx-s, cy-s*0.1, cx+s, cy+s*1.5], start=200, end=340, fill=c, width=w)

def g_mail(draw, cx, cy, s, c):
    w = max(3, int(s*0.14))
    draw.rounded_rectangle([cx-s, cy-s*0.65, cx+s, cy+s*0.65], radius=s*0.12, outline=c, width=w)
    draw.line([(cx-s*0.85, cy-s*0.5), (cx, cy+s*0.05), (cx+s*0.85, cy-s*0.5)], fill=c, width=w, joint="curve")

def g_dot(draw, cx, cy, s, c):
    draw.ellipse([cx-s*0.4, cy-s*0.4, cx+s*0.4, cy+s*0.4], fill=c)

GLYPHS = {
    "phone": g_phone, "shield": g_shield, "bolt": g_bolt, "doc": g_doc,
    "clock": g_clock, "bell": g_bell, "search": g_search, "crown": g_crown,
    "lock": g_lock, "check": g_check, "flag": g_flag, "calendar": g_calendar,
    "scale": g_scale, "car": g_car, "share": g_share, "mail": g_mail, "dot": g_dot,
}

def badge(draw, cx, cy, r, bg, glyph_name, glyph_color=WHITE):
    icon_badge(draw, cx, cy, r, bg, GLYPHS[glyph_name], glyph_color)

# ── Composite UI helpers ─────────────────────────────────────────────────

def phone_shell(draw):
    pill_w, pill_h = 200, 36
    px = (W - pill_w) // 2
    rounded_rect(draw, px, 30, px + pill_w, 30 + pill_h, radius=pill_h // 2, fill=(10, 40, 32, 255))
    draw.text((80, 34), "9:41", font=font(34, bold=True), fill=WHITE)
    draw.text((W - 168, 36), "5G", font=font(26, bold=True), fill=WHITE)
    draw.rounded_rectangle([W-110, 38, W-70, 62], radius=6, outline=WHITE, width=3)
    draw.rectangle([W-68, 44, W-64, 56], fill=WHITE)

def marketing_header(draw, eyebrow, headline, subline, top_color, y_start=118):
    ef = font(32, bold=True)
    ebbox = draw.textbbox((0, 0), eyebrow.upper(), font=ef)
    ew = ebbox[2] - ebbox[0]
    pad = 26
    pill_x0, pill_x1 = (W - ew) // 2 - pad, (W + ew) // 2 + pad
    rounded_rect(draw, pill_x0, y_start, pill_x1, y_start + 54, radius=27, fill=blend(top_color, (255,255,255,255), 0.16))
    draw.text(((W - ew) // 2, y_start + 10), eyebrow.upper(), font=ef, fill=(212, 240, 230, 255))

    y = y_start + 90
    hf = font(96, bold=True)
    for line in headline.split("\n"):
        text_centered(draw, line, y, hf, WHITE)
        bbox = draw.textbbox((0, 0), line, font=hf)
        y += (bbox[3] - bbox[1]) + 20
    y += 14

    sf = font(40)
    y = wrap_text(draw, subline, 0, y, W - 220, sf, (206, 235, 225, 255), center=True)
    return y + 56

def footer_brand(img, draw, y):
    draw.line([(W//2 - 60, y), (W//2 + 60, y)], fill=(255,255,255,60), width=2)
    y += 36
    size = 64
    if os.path.exists(ICON_PATH):
        icon_img = Image.open(ICON_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle([0, 0, size, size], radius=16, fill=255)
        img.paste(icon_img, ((W - size)//2 - 110, y), mask)
    draw.text((W//2 - 34, y + 14), "Malaysia Pocket", font=font(34, bold=True), fill=WHITE)

def stat_strip(draw, cx, y, stats):
    """stats: list of (number, label) — thin horizontal strip of 3 stats."""
    n = len(stats)
    col_w = 1120 // n
    x0 = cx - 560
    for i, (num, label) in enumerate(stats):
        cx_i = x0 + col_w * i + col_w // 2
        nf = font(56, bold=True)
        bbox = draw.textbbox((0,0), num, font=nf)
        draw.text((cx_i - (bbox[2]-bbox[0])//2, y), num, font=nf, fill=WHITE)
        lf = font(26)
        wrap_text(draw, label, 0, y + 74, col_w - 30, lf, (206,235,225,255), center=False)
        # recentre label manually since wrap_text center uses full W
    for i, (num, label) in enumerate(stats):
        pass
    return y + 74 + 70

def stat_strip_centered(draw, cx, y, stats):
    n = len(stats)
    col_w = 1120 // n
    x0 = cx - 560
    for i, (num, label) in enumerate(stats):
        seg_cx = x0 + col_w * i + col_w // 2
        nf = font(58, bold=True)
        bbox = draw.textbbox((0,0), num, font=nf)
        draw.text((seg_cx - (bbox[2]-bbox[0])//2, y), num, font=nf, fill=WHITE)
        lf = font(25)
        # wrap within column, centered on seg_cx
        words = label.split()
        lines, line = [], []
        for word in words:
            test = " ".join(line+[word])
            bb = draw.textbbox((0,0), test, font=lf)
            if bb[2]-bb[0] <= col_w-24:
                line.append(word)
            else:
                lines.append(" ".join(line)); line=[word]
        if line: lines.append(" ".join(line))
        ly = y + 78
        for l in lines:
            bb = draw.textbbox((0,0), l, font=lf)
            draw.text((seg_cx - (bb[2]-bb[0])//2, ly), l, font=lf, fill=(206,235,225,255))
            ly += 34
        if i < n-1:
            div_x = x0 + col_w*(i+1)
            draw.line([(div_x, y+8), (div_x, y+56)], fill=(255,255,255,50), width=2)
    return y + 78 + 34*2 + 20

def row_card(draw, cx, y, w, h, glyph_name, badge_color, title, subtitle=None,
             right_text=None, right_color=URGENT, right_bg=URGENT_BG, right_border=URGENT_BORDER):
    x0, x1 = cx - w//2, cx + w//2
    rounded_rect(draw, x0, y, x1, y+h, radius=22, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    r = h * 0.30
    bcx, bcy = x0 + 32 + r, y + h//2
    badge(draw, bcx, bcy, r, badge_color, glyph_name)
    tx = bcx + r + 26
    if subtitle:
        draw.text((tx, y + h*0.24), title, font=font(36, bold=True), fill=INK)
        draw.text((tx, y + h*0.58), subtitle, font=font(27), fill=MUTED_DARK)
    else:
        draw.text((tx, y + h//2 - 20), title, font=font(36, bold=True), fill=INK)
    if right_text:
        rf = font(25, bold=True)
        bb = draw.textbbox((0,0), right_text, font=rf)
        rw = bb[2]-bb[0] + 26
        rh = 42
        rx1 = x1 - 28
        rounded_rect(draw, rx1-rw, y+h//2-rh//2, rx1, y+h//2+rh//2, radius=rh//2,
                     fill=right_bg, border=right_border, border_width=2)
        draw.text((rx1-rw+13, y+h//2-rh//2+8), right_text, font=rf, fill=right_color)
    return y + h + 18

def section_label(draw, cx, y, title):
    tf = font(30, bold=True)
    draw.text((cx - 560, y), title.upper(), font=tf, fill=(178, 220, 205, 255))
    return y + 54

# ════════════════════════════════════════════════════════════════════════
# 01 — EMERGENCY (hero screen: universal hook, leads the App Store gallery)
# ════════════════════════════════════════════════════════════════════════
def screen_emergency():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, GREEN_DARK, GREEN)
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Malaysia Pocket", "Emergency help,\none tap away",
                          "Police, fire, ambulance and crisis lines — always on your home screen.",
                          GREEN)

    cx = W // 2
    y = section_label(draw, cx, y, "Get help now")
    numbers = [("999", "Police & Ambulance"), ("994", "Fire & Rescue (JBPM)"),
               ("991", "Gas Emergency"), ("15999", "Talian Kasih")]
    col_w, gap = 540, 40
    for i, (num, label) in enumerate(numbers):
        col, row = i % 2, i // 2
        x0 = cx - 560 + col * (col_w + gap)
        yy = y + row * 168
        rounded_rect(draw, x0, yy, x0+col_w, yy+150, radius=22,
                     fill=blend(GREEN, WHITE, 0.14), border=blend(GREEN, WHITE, 0.28), border_width=2)
        badge(draw, x0+80, yy+52, 40, blend(GREEN, WHITE, 0.24), "phone")
        draw.text((x0+140, yy+26), num, font=font(50, bold=True), fill=WHITE)
        draw.text((x0+140, yy+90), label, font=font(27), fill=(215, 240, 230, 255))
    y += 168 * 2 - 18

    y = section_label(draw, cx, y+30, "Something happened")
    y = row_card(draw, cx, y, 1120, 130, "bolt", GREEN, "What happened to you?",
                 "We'll find who handles it and how long you have")

    y = section_label(draw, cx, y+16, "Know your rights & guides")
    y = row_card(draw, cx, y, 1120, 120, "shield", GREEN, "Your rights",
                 "Police stops, work, tenancy, scams")
    y = row_card(draw, cx, y, 1120, 120, "doc", GREEN, "Step-by-step guides",
                 "12 procedures, start to finish")

    y = section_label(draw, cx, y+16, "Community safety")
    y = row_card(draw, cx, y, 1120, 120, "flag", URGENT[:3], "Report an incident",
                 "Reckless driving or road hazards")

    y += 30
    y = stat_strip_centered(draw, cx, y, [("30+", "Situations covered"), ("50+", "Rights topics"), ("12", "Guides")])

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/01_emergency.png", "PNG")
    print("done 01_emergency.png", img.size)


# ════════════════════════════════════════════════════════════════════════
# 02 — KNOW YOUR RIGHTS
# ════════════════════════════════════════════════════════════════════════
def screen_rights():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, GREEN_DARK, GREEN_LIGHT)
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Know Your Rights", "Know your\nrights",
                          "Police stops, tenancy, employment, consumer protection — plain language, real Malaysian law.",
                          GREEN)

    cx = W // 2
    rights = [
        ("shield", "Police stops you", "What you must and need not say · CPC s.28A"),
        ("scale", "Employer deducts salary", "EPF, overtime and leave rights"),
        ("doc", "Landlord enters without notice", "Notice requirements and remedies"),
        ("lock", "Bank calls about your debt", "AKPK, what they can and can't do"),
        ("bolt", "Consumer scam or bad product", "Tribunal Pengguna, time limits"),
        ("flag", "School discipline rights", "Parents and student rights"),
        ("dot", "Voting & elections", "Your rights at the polling station"),
        ("mail", "Social media & online scams", "Reporting to MCMC and PDRM"),
    ]
    for glyph, title, sub in rights:
        y = row_card(draw, cx, y, 1120, 138, glyph, GREEN, title, sub, right_text=None)

    y += 20
    rounded_rect(draw, cx-560, y, cx+560, y+130, radius=22, fill=blend(GREEN_LIGHT, WHITE, 0.12), border=blend(GREEN_LIGHT, WHITE, 0.26), border_width=2)
    wrap_text(draw, "Every right is cited to the actual Malaysian statute — not opinion.",
              cx-500, y+38, 1000, font(32, bold=True), WHITE, center=True)
    y += 150

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/02_rights.png", "PNG")
    print("done 02_rights.png", img.size)


# ════════════════════════════════════════════════════════════════════════
# 03 — DEADLINES (situations)
# ════════════════════════════════════════════════════════════════════════
def screen_deadlines():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, (16, 74, 60, 255)[:3], GREEN)
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Situations", "Know your\ndeadlines",
                          "Every situation shows exactly how long you have — and what to do first.",
                          GREEN)

    cx = W // 2
    situations = [
        ("bolt", "My employer hasn't paid me", "14 days"),
        ("doc", "My landlord kept my deposit", "6 years"),
        ("mail", "I received a demand letter", "7 days"),
        ("car", "I was in a road accident", "3 years"),
        ("flag", "I was unfairly dismissed", "60 days"),
        ("lock", "I received a bankruptcy notice", "7 days"),
        ("scale", "I received an LHDN assessment", "30 days"),
        ("shield", "EPF contribution dispute", "6 months"),
    ]
    for glyph, title, dl in situations:
        y = row_card(draw, cx, y, 1120, 134, glyph, GREEN, title, None,
                      right_text=f"⏳ {dl}".replace("⏳ ", ""), right_color=URGENT, right_bg=URGENT_BG, right_border=URGENT_BORDER)

    y += 16
    rounded_rect(draw, cx-560, y, cx+560, y+140, radius=22, fill=URGENT_BG, border=URGENT_BORDER, border_width=2)
    badge(draw, cx-560+80, y+70, 42, URGENT[:3], "clock")
    draw.text((cx-560+150, y+32), "Most missed deadline", font=font(28, bold=True), fill=(140,60,60,255))
    draw.text((cx-560+150, y+72), "Unfair dismissal — 60 days from termination", font=font(32, bold=True), fill=(120,40,40,255))
    y += 160

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/03_deadlines.png", "PNG")
    print("done 03_deadlines.png", img.size)


# ════════════════════════════════════════════════════════════════════════
# 04 — INCIDENT REPORTING (new)
# ════════════════════════════════════════════════════════════════════════
def screen_incident():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, (18, 46, 40, 255)[:3], (60, 40, 40))
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Incident Reporting", "Report it.\nProtect everyone.",
                          "Reckless driving or an unsafe hazard? Report it to the right agency in seconds.",
                          (60, 40, 40))

    cx = W // 2
    y = section_label(draw, cx, y, "What would you like to report?")
    reports = [
        ("car", "Reckless or dangerous driving", "Reports to JPJ / PDRM"),
        ("bolt", "Road hazard or pothole", "Reports to JKR / local council"),
        ("flag", "Illegal dumping", "Reports to local council (DBKL/MBPJ etc.)"),
        ("shield", "Unsafe construction site", "Reports to DOSH"),
    ]
    for glyph, title, sub in reports:
        y = row_card(draw, cx, y, 1120, 138, glyph, URGENT[:3], title, sub)

    y += 20
    y = section_label(draw, cx, y, "Recent report")
    x0, x1 = cx-560, cx+560
    rounded_rect(draw, x0, y, x1, y+190, radius=24, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    badge(draw, x0+80, y+58, 40, (60, 170, 110), "check")
    draw.text((x0+150, y+30), "Report submitted", font=font(36, bold=True), fill=INK)
    draw.text((x0+150, y+76), "Reckless driving · Federal Highway", font=font(28), fill=MUTED_DARK)
    draw.text((x0+40, y+140), "Reference: JPJ/2026/08/4421", font=font(26, bold=True), fill=(80,150,120,255))
    y += 210

    rounded_rect(draw, cx-560, y, cx+560, y+130, radius=22, fill=blend((60,40,40), WHITE, 0.12), border=blend((60,40,40), WHITE, 0.24), border_width=2)
    wrap_text(draw, "Every report helps build a safer Malaysia for everyone.",
              cx-500, y+38, 1000, font(32, bold=True), WHITE, center=True)
    y += 150

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/04_incident.png", "PNG")
    print("done 04_incident.png", img.size)


# ════════════════════════════════════════════════════════════════════════
# 05 — GUIDES & SEARCH
# ════════════════════════════════════════════════════════════════════════
def screen_guides_search():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, (12, 58, 46, 255)[:3], (38, 116, 96))
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Guides & Search", "Step-by-step,\nstart to finish",
                          "12 full guides, plus instant search across everything the app knows.",
                          GREEN)

    cx = W // 2
    x0, x1 = cx-560, cx+560
    rounded_rect(draw, x0, y, x1, y+92, radius=46, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    badge(draw, x0+58, y+46, 26, GREEN, "search")
    draw.text((x0+108, y+28), "employer didn't pay me", font=font(38), fill=INK)
    y += 92 + 22

    results = [("SITUATION", "My employer hasn't paid me"),
               ("RIGHTS", "Employment and salary rights"),
               ("GUIDE", "File a claim at Industrial Court"),
               ("REPORT", "Labour Department (JTK)")]
    for label, text in results:
        rounded_rect(draw, x0, y, x1, y+96, radius=18, fill=CARD_BG, border=CARD_BORDER, border_width=2)
        draw.text((x0+26, y+16), label, font=font(24, bold=True), fill=GREEN)
        draw.text((x0+26, y+50), text, font=font(33), fill=INK)
        draw.text((x1-46, y+30), "›", font=font(50), fill=MUTED_DARK)
        y += 96 + 14

    y += 16
    y = section_label(draw, cx, y, "Step-by-step guides")
    guides = [
        ("doc", "File a police report", "6 steps"),
        ("mail", "Write a will", "7 steps"),
        ("car", "Contest a traffic summons", "6 steps"),
        ("scale", "File a consumer tribunal claim", "8 steps"),
        ("shield", "Claim EPF after resignation", "5 steps"),
        ("flag", "Register a business (SSM)", "4 steps"),
    ]
    for glyph, title, steps in guides:
        y = row_card(draw, cx, y, 1120, 122, glyph, GREEN, title, None,
                      right_text=steps, right_color=GREEN, right_bg=blend(WHITE,(*GREEN,255),0.12), right_border=CARD_BORDER)

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/05_guides_search.png", "PNG")
    print("done 05_guides_search.png", img.size)


# ════════════════════════════════════════════════════════════════════════
# 06 — CASE TRACKER (Pro)
# ════════════════════════════════════════════════════════════════════════
def screen_tracking():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, (20, 84, 68, 255)[:3], GREEN)
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Case Tracker · Pro", "Never miss\na deadline",
                          "Track any case with local reminders — 30, 7, and 1 day before it's due.",
                          GREEN)

    cx = W // 2
    x0, x1 = cx-560, cx+560

    rounded_rect(draw, x0, y, x1, y+420, radius=28, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    draw.text((x0+40, y+34), "Unfair dismissal", font=font(42, bold=True), fill=INK)
    draw.text((x0+40, y+86), "Industrial Relations Act 1967", font=font(26), fill=MUTED_DARK)

    ring_cx, ring_cy = cx, y+250
    draw.ellipse([ring_cx-130, ring_cy-130, ring_cx+130, ring_cy+130], outline=CARD_BORDER, width=18)
    draw.arc([ring_cx-130, ring_cy-130, ring_cx+130, ring_cy+130], start=-90, end=int(-90+360*(47/60)), fill=URGENT[:3], width=18)
    draw.text((ring_cx-72, ring_cy-58), "47", font=font(96, bold=True), fill=URGENT[:3])
    draw.text((ring_cx-78, ring_cy+48), "days left", font=font(30), fill=MUTED_DARK)

    draw.text((x0+40, y+392-2), "Due 29 September 2026", font=font(28), fill=MUTED_DARK)
    y += 420 + 24

    rounded_rect(draw, x0, y, x1, y+150, radius=20, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    draw.text((x0+36, y+24), "Notes", font=font(28, bold=True), fill=MUTED_DARK)
    wrap_text(draw, "Sent demand letter on 3 Aug. HR replied requesting a meeting on 10 Aug.",
              x0+36, y+64, 1040, font(32), INK)
    y += 170

    rounded_rect(draw, x0, y, x1, y+108, radius=20, fill=blend(GREEN, WHITE, 0.14), border=blend(GREEN, WHITE, 0.26), border_width=2)
    badge(draw, x0+70, y+54, 32, blend(GREEN, WHITE, 0.24), "bell")
    draw.text((x0+120, y+34), "Reminder set for 22 September 2026", font=font(30, bold=True), fill=WHITE)
    y += 128

    y = section_label(draw, cx, y+10, "Other tracked cases")
    rounded_rect(draw, x0, y, x1, y+118, radius=20, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    draw.text((x0+34, y+22), "Wage claim (JTK)", font=font(34, bold=True), fill=INK)
    draw.text((x0+34, y+64), "Submitted 22 Jul · due 5 Aug", font=font(26), fill=MUTED_DARK)
    rounded_rect(draw, x1-160, y+34, x1-30, y+80, radius=23, fill=(230,248,240,255), border=(170,220,200,255), border_width=2)
    draw.text((x1-148, y+44), "Filed", font=font(24, bold=True), fill=(50,140,100,255))
    y += 140

    rounded_rect(draw, x0, y, x1, y+96, radius=20, fill=GOLD_BG, border=GOLD_BORDER, border_width=2)
    badge(draw, x0+56, y+48, 26, GOLD[:3], "crown")
    draw.text((x0+100, y+30), "Pocket Pro · deadline tracking & reminders", font=font(28, bold=True), fill=(120,90,20,255))
    y += 116

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/06_tracking.png", "PNG")
    print("done 06_tracking.png", img.size)


# ════════════════════════════════════════════════════════════════════════
# 07 — POCKET PRO (complaint letter + upsell)
# ════════════════════════════════════════════════════════════════════════
def screen_pro():
    img = Image.new("RGBA", (W, H), (*GREEN, 255))
    gradient_bg(img, (8, 44, 36, 255)[:3], (20, 84, 68))
    draw = ImageDraw.Draw(img, "RGBA")
    phone_shell(draw)

    y = marketing_header(draw, "Pocket Pro", "Unlock the\nfull toolkit",
                          "Ad-free. Auto-generated complaint letters. Deadline tracking with reminders.",
                          (20, 84, 68))

    cx = W // 2
    x0, x1 = cx-560, cx+560

    rounded_rect(draw, x0, y, x1, y+330, radius=28, fill=GOLD_BG, border=GOLD_BORDER, border_width=3)
    badge(draw, x0+70, y+66, 34, GOLD[:3], "crown")
    draw.text((x0+130, y+40), "Pocket Pro", font=font(46, bold=True), fill=(140,105,25,255))
    draw.text((x0+40, y+114), "Everything, forever.", font=font(34), fill=(90,68,20,255))
    feats = ["Ad-free experience", "Generate complaint letters (BM & EN)",
             "Track deadlines with reminders", "Export your cases as JSON"]
    fy = y + 172
    for feat in feats:
        badge(draw, x0+56, fy+18, 16, (196,150,46,255), "check")
        draw.text((x0+92, fy), feat, font=font(30), fill=(70,55,20,255))
        fy += 42
    y += 330 + 26

    y = section_label(draw, cx, y, "Complaint letter — auto-generated")
    rounded_rect(draw, x0, y, x1, y+380, radius=22, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    lines = [
        ("Kepada Yang Berhormat,", font(32, bold=True), INK),
        ("Pengarah, Jabatan Buruh", font(28), MUTED_DARK),
        ("", None, None),
        ("Saya, Ahmad bin Abdullah (IC: 880101-01-1234),", font(27), INK),
        ("ingin membuat aduan terhadap majikan saya", font(27), INK),
        ("berkenaan gaji yang tidak dibayar selama 3 bulan.", font(27), INK),
        ("", None, None),
        ("Jumlah terhutang: RM 4,500", font(30, bold=True), (150,110,20,255)),
        ("untuk bulan Mei–Julai 2026.", font(27), INK),
    ]
    ly = y + 32
    for text, fnt, col in lines:
        if text and fnt:
            draw.text((x0+38, ly), text, font=fnt, fill=col)
            ly += 40
        else:
            ly += 18
    y += 400

    btn_w, gap = (1120-40)//2, 40
    actions = [("share", "Share", GREEN[:3]), ("doc", "Copy", GREEN_DARK), ("mail", "Email", (16,70,56))]
    bw3 = (1120 - gap*2)//3
    for i, (glyph, label, col) in enumerate(actions):
        bx0 = x0 + i*(bw3+gap)
        bx1 = bx0+bw3
        rounded_rect(draw, bx0, y, bx1, y+108, radius=22, fill=col)
        badge(draw, bx0+bw3//2-70, y+54, 24, blend(col,(255,255,255,255),0.25), glyph)
        draw.text((bx0+bw3//2-20, y+38), label, font=font(32, bold=True), fill=WHITE)
    y += 128

    footer_brand(img, draw, H - 150)
    img.convert("RGB").save(f"{OUT}/07_pro.png", "PNG")
    print("done 07_pro.png", img.size)


if __name__ == "__main__":
    for f in os.listdir(OUT):
        if f.endswith(".png"):
            os.remove(os.path.join(OUT, f))
    screen_emergency()
    screen_rights()
    screen_deadlines()
    screen_incident()
    screen_guides_search()
    screen_tracking()
    screen_pro()
    print(f"\nAll screenshots saved to {OUT}/")
