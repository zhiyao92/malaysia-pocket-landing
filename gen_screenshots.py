#!/usr/bin/env python3
"""
Generates 6.9-inch App Store marketing screenshots for Malaysia Pocket.
Canvas: 1320 × 2868 px (iPhone 16 Pro Max portrait).
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

OUT = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT, exist_ok=True)

W, H = 1320, 2868

# Brand colours
GREEN      = (31, 111, 92)       # #1F6F5C accent
GREEN_DARK = (18, 76, 62)        # darker shade for gradients
GREEN_LIGHT= (45, 148, 122)      # lighter shade
WHITE      = (255, 255, 255)
OFF_WHITE  = (247, 250, 248)
MUTED      = (130, 165, 155)
CARD_BG    = (255, 255, 255)
CARD_BORDER= (220, 238, 232)
URGENT     = (205, 92, 92)       # red-ish for deadlines
GOLD       = (201, 155, 48)

# ── helpers ──────────────────────────────────────────────────────────────────

def font(size, bold=False):
    """Return a system font at the given size."""
    candidates_bold = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFPro-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFPro-Regular.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in (candidates_bold if bold else candidates):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def text_centered(draw, text, y, fnt, color=WHITE, max_width=None):
    """Draw text horizontally centred on the canvas."""
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, font=fnt, fill=color)
    return bbox[3] - bbox[1]   # returns text height

def wrap_text(draw, text, x, y, max_width, fnt, color, line_spacing=1.35):
    """Wrap text to fit max_width, return bottom y."""
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
        draw.text((x, y + i * int(fnt.size * line_spacing)), l, font=fnt, fill=color)
    return y + len(lines) * int(fnt.size * line_spacing)

def gradient_bg(img, top_color, bottom_color):
    """Fill img with a vertical gradient."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(top_color[0] * (1-t) + bottom_color[0] * t)
        g = int(top_color[1] * (1-t) + bottom_color[1] * t)
        b = int(top_color[2] * (1-t) + bottom_color[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def rounded_rect(draw, x0, y0, x1, y1, radius, fill, border=None, border_width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                            outline=border, width=border_width)

def pill(draw, x0, y0, x1, y1, fill, text, fnt, text_color=WHITE):
    rounded_rect(draw, x0, y0, x1, y1, radius=(y1-y0)//2, fill=fill)
    bbox = draw.textbbox((0,0), text, font=fnt)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((x0+x1-tw)//2, (y0+y1-th)//2 - 2), text, font=fnt, fill=text_color)

def card(draw, cx, y, width, height, title, subtitle=None,
         icon=None, badge_text=None, badge_color=GREEN):
    """Draw a single list row card."""
    x0 = cx - width // 2
    x1 = cx + width // 2
    rounded_rect(draw, x0, y, x1, y+height, radius=24,
                 fill=CARD_BG, border=CARD_BORDER, border_width=2)
    pad = 40
    ty = y + height//2 - 18
    if subtitle:
        ty = y + 30
    if icon:
        draw.text((x0+pad, ty), icon, font=font(44), fill=GREEN)
    title_x = x0 + pad + (70 if icon else 0)
    draw.text((title_x, ty), title, font=font(38, bold=True), fill=(30,50,45))
    if subtitle:
        draw.text((title_x, ty+52), subtitle, font=font(30), fill=MUTED)
    if badge_text:
        bfnt = font(24, bold=True)
        bbbox = draw.textbbox((0,0), badge_text, font=bfnt)
        bw = bbbox[2]-bbbox[0] + 28
        bh = 36
        bx0 = x1 - bw - pad
        by0 = y + height//2 - bh//2
        rounded_rect(draw, bx0, by0, bx0+bw, by0+bh,
                     radius=bh//2, fill=badge_color)
        draw.text((bx0+14, by0+4), badge_text, font=bfnt, fill=WHITE)

def clock_badge(draw, cx, y, limit_text, from_text):
    """Red deadline badge block."""
    x0 = cx - 560
    x1 = cx + 560
    rounded_rect(draw, x0, y, x1, y+120, radius=20,
                 fill=(255, 245, 245), border=(220, 180, 180), border_width=2)
    draw.text((x0+30, y+18), "⏱", font=font(50), fill=URGENT)
    draw.text((x0+100, y+16), limit_text, font=font(46, bold=True), fill=URGENT)
    draw.text((x0+100, y+68), from_text, font=font(30), fill=(150, 80, 80))

def section_header(draw, cx, y, title):
    tf = font(32, bold=True)
    bbox = draw.textbbox((0,0), title.upper(), font=tf)
    draw.text((cx - 560, y), title.upper(), font=tf, fill=MUTED)

def progress_bar(draw, cx, y, value, total, label):
    x0, x1 = cx-560, cx+560
    bh = 12
    rounded_rect(draw, x0, y, x1, y+bh, radius=6, fill=(200, 230, 220))
    fill_w = int((x1-x0) * value / max(total, 1))
    if fill_w > 12:
        rounded_rect(draw, x0, y, x0+fill_w, y+bh, radius=6, fill=GREEN)
    draw.text((x0, y+20), label, font=font(28), fill=MUTED)

def checklist_item(draw, x, y, text, checked=False):
    icon = "✓" if checked else "○"
    color = GREEN if checked else MUTED
    draw.text((x, y), icon, font=font(36, bold=True), fill=color)
    draw.text((x+60, y+2), text, font=font(34),
              fill=(30,50,45) if not checked else MUTED)

def search_result_row(draw, cx, y, section_label, result_text):
    x0, x1 = cx-560, cx+560
    rounded_rect(draw, x0, y, x1, y+90, radius=16,
                 fill=CARD_BG, border=CARD_BORDER, border_width=1)
    draw.text((x0+24, y+12), section_label, font=font(24, bold=True), fill=GREEN)
    draw.text((x0+24, y+44), result_text, font=font(32), fill=(30,50,45))
    # chevron
    draw.text((x1-50, y+28), "›", font=font(48), fill=MUTED)

# ── SCREEN FACTORY ───────────────────────────────────────────────────────────

def phone_shell(img):
    """Draw a subtle phone status bar area at the top."""
    draw = ImageDraw.Draw(img)
    # dynamic island pill
    pill_w, pill_h = 200, 36
    px = (W - pill_w) // 2
    rounded_rect(draw, px, 28, px+pill_w, 28+pill_h, radius=pill_h//2,
                 fill=(10, 60, 45))
    # time
    draw.text((80, 32), "9:41", font=font(34, bold=True), fill=WHITE)
    # battery icons (simplified)
    draw.text((W-160, 32), "●●●●", font=font(26), fill=WHITE)

def marketing_header(draw, eyebrow, headline, subline=None, y_start=120):
    """Top marketing text block."""
    # eyebrow
    ef = font(34, bold=True)
    ebbox = draw.textbbox((0,0), eyebrow.upper(), font=ef)
    ew = ebbox[2]-ebbox[0]
    # pill behind eyebrow
    pad = 24
    pill_x0 = (W-ew-pad*2)//2
    pill_x1 = (W+ew+pad*2)//2
    rounded_rect(draw, pill_x0, y_start, pill_x1, y_start+52,
                 radius=26, fill=(255,255,255,50))
    draw.text(((W-ew)//2, y_start+8), eyebrow.upper(), font=ef,
              fill=(200, 235, 225))

    y = y_start + 80
    hf = font(92, bold=True)
    for line in headline.split("\n"):
        text_centered(draw, line, y, hf, WHITE)
        bbox = draw.textbbox((0,0), line, font=hf)
        y += (bbox[3]-bbox[1]) + 16
    y += 10

    if subline:
        sf = font(44)
        wrap_text(draw, subline, 100, y, W-200, sf, (200, 235, 225))
        bbox = draw.textbbox((0,0), subline, font=sf)
        y += (bbox[3]-bbox[1]) + 40

    return y + 30


# ════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 1 — Home / Get Help Now
# ════════════════════════════════════════════════════════════════════════════
def screen_home():
    img = Image.new("RGB", (W, H), GREEN)
    gradient_bg(img, GREEN_DARK, GREEN)
    draw = ImageDraw.Draw(img)

    phone_shell(img)
    content_y = marketing_header(
        draw,
        eyebrow="Malaysia Pocket",
        headline="Your legal\ncompanion",
        subline="Emergency numbers, deadlines, rights — everything Malaysians need in one place.",
        y_start=120
    )

    # simulate home screen UI
    cx = W // 2

    # "Get help now" section
    section_header(draw, cx, content_y, "Get help now")
    content_y += 52

    emergency_numbers = [
        ("999", "Police & Emergency"),
        ("994", "Fire & Rescue"),
        ("999", "Hospital Emergency"),
    ]
    for i, (num, label) in enumerate(emergency_numbers[:2]):
        x0 = cx - 560 + i * 590
        x1 = x0 + 540
        rounded_rect(draw, x0, content_y, x1, content_y+110,
                     radius=22, fill=(255,255,255,25))
        draw.text((x0+24, content_y+14), "📞", font=font(42), fill=WHITE)
        draw.text((x0+80, content_y+10), num, font=font(46, bold=True), fill=WHITE)
        draw.text((x0+24, content_y+64), label, font=font(28), fill=(200,235,225))

    content_y += 140

    # "Something happened" section
    section_header(draw, cx, content_y, "Something happened")
    content_y += 52
    card(draw, cx, content_y, 1120, 120,
         "What happened to you?",
         "Find who handles it, what you need, and how long you have",
         icon="⚡")
    content_y += 140

    # "Know your rights" section
    section_header(draw, cx, content_y, "Know your rights")
    content_y += 52
    card(draw, cx, content_y, 1120, 110,
         "Your rights",
         "Police stops, work, tenancy, scams", icon="🛡")
    content_y += 130
    card(draw, cx, content_y, 1120, 110,
         "Step-by-step guides",
         "12 procedures, start to finish", icon="📋")

    img.save(f"{OUT}/01_home.png", "PNG")
    print("✓ 01_home.png")


# ════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 2 — Situations / Know Your Deadline
# ════════════════════════════════════════════════════════════════════════════
def screen_situations():
    img = Image.new("RGB", (W, H), GREEN)
    gradient_bg(img, (18, 76, 62), (31, 111, 92))
    draw = ImageDraw.Draw(img)
    phone_shell(img)

    content_y = marketing_header(
        draw,
        eyebrow="Situations",
        headline="Know your\ndeadlines",
        subline="Every situation shows how long you have and what happens if you miss it.",
        y_start=120
    )

    cx = W // 2
    situations = [
        ("My employer hasn't paid me", "14 days from last day of employment", "⏱"),
        ("My landlord kept my deposit", "3 years from date of dispute", "⏱"),
        ("I received a demand letter", "7 days to respond", "⏱"),
        ("I was in a road accident", "3 years from accident date", "⏱"),
        ("I was unfairly dismissed", "60 days from dismissal", "⏱"),
        ("I received a bankruptcy notice", "7 days to respond", "⏱"),
    ]

    for i, (title, deadline, icon) in enumerate(situations):
        y = content_y + i * 155
        x0 = cx - 560
        x1 = cx + 560
        rounded_rect(draw, x0, y, x1, y+140, radius=20,
                     fill=CARD_BG, border=CARD_BORDER, border_width=2)
        draw.text((x0+30, y+22), title, font=font(36, bold=True), fill=(25,55,45))
        # deadline chip
        df = font(26, bold=True)
        dbbox = draw.textbbox((0,0), deadline, font=df)
        dw = dbbox[2]-dbbox[0]+24
        rounded_rect(draw, x0+30, y+76, x0+30+dw, y+76+38,
                     radius=19, fill=(255, 245, 240), border=(220,180,180))
        draw.text((x0+42, y+82), deadline, font=df, fill=URGENT)
        # chevron
        draw.text((x1-60, y+46), "›", font=font(60), fill=GREEN)

    img.save(f"{OUT}/02_situations.png", "PNG")
    print("✓ 02_situations.png")


# ════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 3 — Case Tracking
# ════════════════════════════════════════════════════════════════════════════
def screen_tracking():
    img = Image.new("RGB", (W, H), GREEN)
    gradient_bg(img, (22, 90, 72), (31, 111, 92))
    draw = ImageDraw.Draw(img)
    phone_shell(img)

    content_y = marketing_header(
        draw,
        eyebrow="Case Tracker",
        headline="Never miss\na deadline",
        subline="Track any case. Get local notifications before your time runs out.",
        y_start=120
    )

    cx = W // 2

    # Big case card
    x0, x1 = cx-560, cx+560
    rounded_rect(draw, x0, content_y, x1, content_y+380, radius=28,
                 fill=CARD_BG, border=CARD_BORDER, border_width=2)

    draw.text((x0+40, content_y+30), "My employer hasn't paid me",
              font=font(40, bold=True), fill=(25,55,45))

    # Countdown ring (simplified)
    countdown_y = content_y + 110
    ring_cx, ring_cy = cx, countdown_y + 80
    # outer ring
    draw.ellipse([ring_cx-120, ring_cy-120, ring_cx+120, ring_cy+120],
                 outline=CARD_BORDER, width=16)
    # progress arc (8 days left of 14)
    draw.arc([ring_cx-120, ring_cy-120, ring_cx+120, ring_cy+120],
             start=-90, end=int(-90 + 360*(8/14)), fill=GREEN, width=16)
    draw.text((ring_cx-60, ring_cy-60), "8", font=font(100, bold=True), fill=GREEN)
    draw.text((ring_cx-70, ring_cy+40), "days left", font=font(32), fill=MUTED)

    draw.text((x0+40, content_y+320), "Deadline: 19 August 2026",
              font=font(30), fill=MUTED)

    content_y += 400 + 30

    # Notes field
    rounded_rect(draw, x0, content_y, x1, content_y+130, radius=20,
                 fill=CARD_BG, border=CARD_BORDER, border_width=2)
    draw.text((x0+40, content_y+20), "Notes", font=font(30, bold=True), fill=MUTED)
    draw.text((x0+40, content_y+62), "Sent demand letter on 3 Aug. HR replied...",
              font=font(34), fill=(30,55,45))

    content_y += 150 + 20

    # Reminder badge
    rounded_rect(draw, x0, content_y, x1, content_y+100, radius=20,
                 fill=(240, 252, 246), border=(160, 210, 195), border_width=2)
    draw.text((x0+40, content_y+28), "🔔  Reminder set for 12 August 2026",
              font=font(36), fill=GREEN)

    # Bottom notification card
    content_y += 120 + 30
    rounded_rect(draw, x0, content_y, x1, content_y+110, radius=20,
                 fill=(255,248,235), border=(220,195,140), border_width=2)
    draw.text((x0+40, content_y+18), "Pocket Pro", font=font(30, bold=True), fill=GOLD)
    draw.text((x0+40, content_y+56), "Track deadlines & get reminded before they expire",
              font=font(32), fill=(80,60,20))

    img.save(f"{OUT}/03_tracking.png", "PNG")
    print("✓ 03_tracking.png")


# ════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 4 — Know Your Rights
# ════════════════════════════════════════════════════════════════════════════
def screen_rights():
    img = Image.new("RGB", (W, H), GREEN)
    gradient_bg(img, GREEN_DARK, GREEN_LIGHT)
    draw = ImageDraw.Draw(img)
    phone_shell(img)

    content_y = marketing_header(
        draw,
        eyebrow="Know Your Rights",
        headline="Rights you\nshould know",
        subline="Police stops, tenancy, employment, consumer protection — plain language, not legalese.",
        y_start=120
    )

    cx = W // 2
    rights = [
        ("Police stops you", "What you must and need not say", "🛡"),
        ("Employer deducts salary", "EPF, overtime and leave rights", "💼"),
        ("Landlord enters without notice", "Notice requirements and remedies", "🏠"),
        ("Bank calls about debt", "AKPK, what they can and can't do", "🏦"),
        ("Consumer scam / bad product", "TTPM, tribunal, time limits", "🛒"),
        ("School discipline rights", "Parents and student rights", "🎓"),
    ]

    for i, (title, sub, icon) in enumerate(rights):
        y = content_y + i * 148
        x0, x1 = cx-560, cx+560
        rounded_rect(draw, x0, y, x1, y+132, radius=20,
                     fill=CARD_BG, border=CARD_BORDER, border_width=2)
        draw.text((x0+24, y+20), icon, font=font(50), fill=GREEN)
        draw.text((x0+100, y+16), title, font=font(38, bold=True), fill=(25,55,45))
        draw.text((x0+100, y+66), sub, font=font(30), fill=MUTED)
        draw.text((x1-58, y+38), "›", font=font(60), fill=GREEN)

    img.save(f"{OUT}/04_rights.png", "PNG")
    print("✓ 04_rights.png")


# ════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 5 — Guides + Search
# ════════════════════════════════════════════════════════════════════════════
def screen_guides_search():
    img = Image.new("RGB", (W, H), GREEN)
    gradient_bg(img, (14, 65, 52), (40, 120, 100))
    draw = ImageDraw.Draw(img)
    phone_shell(img)

    content_y = marketing_header(
        draw,
        eyebrow="Guides & Search",
        headline="Step-by-step,\nstart to finish",
        subline="12 guides and instant search across every situation, right, and complaint channel.",
        y_start=120
    )

    cx = W // 2

    # Search bar mock
    sb_x0, sb_x1 = cx-560, cx+560
    rounded_rect(draw, sb_x0, content_y, sb_x1, content_y+88,
                 radius=44, fill=CARD_BG, border=CARD_BORDER, border_width=2)
    draw.text((sb_x0+36, content_y+22), "🔍", font=font(40), fill=MUTED)
    draw.text((sb_x0+100, content_y+26), "employer didn't pay me",
              font=font(38), fill=(30,55,45))

    content_y += 100 + 24

    # Search results
    results = [
        ("SITUATION", "My employer hasn't paid me"),
        ("RIGHTS", "Employment and salary rights"),
        ("GUIDE", "File a claim at Industrial Court"),
        ("COMPLAINT", "Labour Department (JTK)"),
    ]
    for section, text in results:
        search_result_row(draw, cx, content_y, section, text)
        content_y += 104

    content_y += 20

    # Guide list preview
    section_header(draw, cx, content_y, "Step-by-step guides")
    content_y += 52

    guides = [
        ("File a police report", "6 steps", "📋"),
        ("Write a will", "7 steps", "📝"),
        ("Contest a traffic summons", "6 steps", "🚗"),
        ("File a consumer tribunal claim", "8 steps", "⚖️"),
    ]
    for title, steps, icon in guides:
        x0, x1 = cx-560, cx+560
        rounded_rect(draw, x0, content_y, x1, content_y+110, radius=18,
                     fill=CARD_BG, border=CARD_BORDER, border_width=2)
        draw.text((x0+24, content_y+22), icon, font=font(46), fill=GREEN)
        draw.text((x0+95, content_y+16), title, font=font(36, bold=True), fill=(25,55,45))
        sf = font(26, bold=True)
        sbbox = draw.textbbox((0,0), steps, font=sf)
        sw = sbbox[2]-sbbox[0]+20
        rounded_rect(draw, x1-sw-30, content_y+36, x1-30, content_y+36+38,
                     radius=19, fill=(230,245,240))
        draw.text((x1-sw-20, content_y+42), steps, font=sf, fill=GREEN)
        content_y += 126

    img.save(f"{OUT}/05_guides_search.png", "PNG")
    print("✓ 05_guides_search.png")


# ════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 6 — Pocket Pro (Premium)
# ════════════════════════════════════════════════════════════════════════════
def screen_pro():
    img = Image.new("RGB", (W, H), GREEN)
    gradient_bg(img, (10, 48, 38), (22, 88, 70))
    draw = ImageDraw.Draw(img)
    phone_shell(img)

    # Gold-tinted header for premium feel
    content_y = marketing_header(
        draw,
        eyebrow="Pocket Pro",
        headline="Unlock the\nfull toolkit",
        subline="Ad-free. Complaint letters. Deadline tracking with reminders.",
        y_start=120
    )

    cx = W // 2

    # Big premium card
    x0, x1 = cx-560, cx+560
    rounded_rect(draw, x0, content_y, x1, content_y+300, radius=28,
                 fill=(255, 252, 240), border=(200, 170, 80), border_width=3)

    draw.text((x0+40, content_y+30), "👑  Pocket Pro", font=font(48, bold=True), fill=GOLD)
    draw.text((x0+40, content_y+90), "Everything, forever.", font=font(36), fill=(80,60,20))

    pro_features = [
        "✓  Ad-free experience",
        "✓  Generate complaint letters (BM & EN)",
        "✓  Track deadlines with reminders",
        "✓  Export your cases as JSON",
    ]
    fy = content_y + 150
    for feat in pro_features:
        draw.text((x0+40, fy), feat, font=font(34), fill=(40,35,15))
        fy += 48

    content_y += 320 + 28

    # Letter preview
    section_header(draw, cx, content_y, "Complaint letter — auto-generated")
    content_y += 52

    rounded_rect(draw, x0, content_y, x1, content_y+340, radius=20,
                 fill=CARD_BG, border=CARD_BORDER, border_width=2)

    letter_lines = [
        ("Kepada Yang Berhormat,", font(32, bold=True), (25,55,45)),
        ("Pengarah, Jabatan Buruh", font(30), MUTED),
        ("", None, None),
        ("Saya, Ahmad bin Abdullah (IC: 880101-01-1234),", font(28), (25,55,45)),
        ("ingin membuat aduan terhadap majikan saya", font(28), (25,55,45)),
        ("berkenaan gaji yang tidak dibayar selama 3 bulan.", font(28), (25,55,45)),
        ("", None, None),
        ("Jumlah terhutang: RM 4,500 untuk bulan Mei–Julai 2026.", font(28), (25,55,45)),
    ]
    ly = content_y + 30
    for line_text, line_font, line_color in letter_lines:
        if line_text and line_font:
            draw.text((x0+40, ly), line_text, font=line_font, fill=line_color)
            ly += 36
        else:
            ly += 18

    content_y += 360 + 28

    # Share / copy actions
    btn_w = 520
    for i, (label, icon, col) in enumerate([
        ("Copy letter", "📋", GREEN),
        ("Share or email", "📤", GREEN_DARK),
    ]):
        bx0 = cx - 560 + i * (btn_w + 40)
        bx1 = bx0 + btn_w
        rounded_rect(draw, bx0, content_y, bx1, content_y+90, radius=20, fill=col)
        draw.text((bx0+30, content_y+22), icon, font=font(38), fill=WHITE)
        draw.text((bx0+90, content_y+26), label, font=font(36, bold=True), fill=WHITE)

    img.save(f"{OUT}/06_pro.png", "PNG")
    print("✓ 06_pro.png")


if __name__ == "__main__":
    screen_home()
    screen_situations()
    screen_tracking()
    screen_rights()
    screen_guides_search()
    screen_pro()
    print(f"\nAll screenshots saved to {OUT}/")
