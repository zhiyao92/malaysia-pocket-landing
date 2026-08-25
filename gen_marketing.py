"""
Malaysia Pocket — App Store marketing screenshot generator.
Takes real simulator screenshots and adds a branded header strip.
Output: 1320x2868px RGB PNG (6.9-inch App Store Connect spec).
"""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

W, H = 1320, 2868
HEADER_H = 480          # header strip height (real screenshot fills the rest)
SCREEN_H = H - HEADER_H # 2388px of real UI

SRC = "real-screenshots"
OUT = "screenshots"
os.makedirs(OUT, exist_ok=True)

# Brand colours (from AppTheme)
GREEN      = (40, 120, 80)
GREEN_DARK = (20,  70, 45)
WHITE      = (255, 255, 255)
OFF_WHITE  = (230, 240, 235)

def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFPro-Display.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                idx = 1 if (bold and p.endswith(".ttc")) else 0
                return ImageFont.truetype(p, size, index=idx)
            except Exception:
                continue
    return ImageFont.load_default()

def gradient_rect(img, y0, y1, top_color, bot_color):
    """Vertical gradient from top_color to bot_color between y0 and y1."""
    draw = ImageDraw.Draw(img)
    for y in range(y0, y1):
        t = (y - y0) / max(y1 - y0 - 1, 1)
        r = int(top_color[0] * (1-t) + bot_color[0] * t)
        g = int(top_color[1] * (1-t) + bot_color[1] * t)
        b = int(top_color[2] * (1-t) + bot_color[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def make_screenshot(src_file, out_file, headline, subline):
    src_path = os.path.join(SRC, src_file)
    if not os.path.exists(src_path):
        print(f"  SKIP (missing): {src_path}")
        return

    # Load real screenshot and crop to SCREEN_H from top
    real = Image.open(src_path).convert("RGB")
    real_w, real_h = real.size
    # Scale if needed (should already be 1320 wide)
    if real_w != W:
        real = real.resize((W, int(real_h * W / real_w)), Image.LANCZOS)
    # Crop to SCREEN_H from top
    real_cropped = real.crop((0, 0, W, min(SCREEN_H, real.height)))

    # Canvas
    canvas = Image.new("RGB", (W, H), GREEN_DARK)

    # Header gradient
    gradient_rect(canvas, 0, HEADER_H, GREEN_DARK, GREEN)

    # Paste real screenshot below header
    canvas.paste(real_cropped, (0, HEADER_H))

    draw = ImageDraw.Draw(canvas)

    # App name pill
    pill_font = load_font(32, bold=False)
    app_label = "Malaysia Pocket"
    tw = draw.textlength(app_label, font=pill_font)
    px, py, pr = 66, 72, 14
    draw.rounded_rectangle([px, py, px + tw + pr*2, py + 52], radius=26,
                            fill=None, outline=(200, 230, 210), width=2)
    draw.text((px + pr, py + 10), app_label, font=pill_font, fill=(200, 230, 210))

    # Headline (bold, large)
    h_font = load_font(88, bold=True)
    # Wrap to ~18 chars per line
    lines = textwrap.wrap(headline, width=18)
    y = 152
    for line in lines:
        draw.text((66, y), line, font=h_font, fill=WHITE)
        y += 106

    # Subline
    sub_font = load_font(46)
    sub_lines = textwrap.wrap(subline, width=30)
    y += 10
    for line in sub_lines:
        draw.text((66, y), line, font=sub_font, fill=(*OFF_WHITE, 210))
        y += 60

    # Thin separator line between header and screenshot
    draw.line([(0, HEADER_H), (W, HEADER_H)], fill=(*GREEN_DARK, 180), width=3)

    out_path = os.path.join(OUT, out_file)
    canvas.convert("RGB").save(out_path, "PNG")
    print(f"  ✓ {out_path}  ({canvas.width}×{canvas.height})")

screens = [
    ("01_home.png",            "01_emergency.png",
     "Emergency.\nOne tap.",
     "999, 994, 997, 991 — always visible on your home screen"),

    ("02_situations.png",      "02_situations.png",
     "Something\nhappened?",
     "Find what to do, who handles it, and how long you have"),

    ("03_situation_detail.png","03_deadline.png",
     "Your deadline.\nRight there.",
     "Never miss the legal window to file your claim"),

    ("04_rights.png",          "04_rights.png",
     "Know your\nrights.",
     "Police stops, workplace, tenancy, scams and more"),

    ("05_guides.png",          "05_guides.png",
     "Step by step.\nNo lawyer needed.",
     "29 procedures from scam recovery to police reports"),

    ("06_report.png",          "06_complaint.png",
     "Report it to\nthe right agency.",
     "Direct links to SPRM, NSRC, SKMM and more"),
]

print(f"Generating {len(screens)} marketing screenshots…")
for src, out, headline, subline in screens:
    print(f"  {src} → {out}")
    make_screenshot(src, out, headline, subline)
print("Done.")
