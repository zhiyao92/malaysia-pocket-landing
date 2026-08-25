# Malaysia Pocket — landing page

Static landing page for the **Malaysia Pocket** iOS app (the app itself lives in
`../Malaysia-Law-101/`), plus the Python generators that produce its App Store and
marketing imagery. Its own GitHub repo: `zhiyao92/malaysia-pocket-landing`.

## Build & run
- **No build step.** `index.html` is the whole page — open it directly, or
  `python3 -m http.server` in this folder to preview.
- Image generators (Python 3 + Pillow):
  - `gen_appstore.py` — App Store screenshots, 1320×2868 (6.9", iPhone 17/16 Pro Max),
    flat RGB PNG with no alpha, which is what App Store Connect accepts.
  - `gen_screenshots.py` — device screenshots for the page.
  - `gen_marketing.py` — social/marketing images.

## Structure
- `index.html` — the page.
- `app-icon.png` — exported from the app's asset catalog.
- `real-screenshots/`, `real-screenshots-v2/` — captures from the Simulator, the input to
  the generators.
- `screenshots/`, `appstore-6.9/` — generated output. Treat as build artifacts.

## Conventions & notes
- **The imagery follows the app's design system, not a separate marketing one:** flat colour
  fields, no gradients, no drop shadows, SF Pro throughout. Deep forest green is the canvas,
  `accent` marks the eyebrow.
- **Red is emergency-only** — exactly one frame uses `urgent` red, the emergency one, because
  red carries that meaning inside the app. Don't spread it for visual variety.
- Capture new source screenshots with the `sim-verify` skill against `Malaysia-Law-101/`,
  drop them in `real-screenshots-v2/`, then re-run the generator — don't hand-edit output.
- Separate repo from the app; a change here is not a change to Malaysia Pocket.
