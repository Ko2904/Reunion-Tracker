"""Leonie & Ko Reunion Tracker
Run with:  streamlit run app.py
"""

import base64
import io
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

APP_TITLE = "Leonie & Ko Reunion Tracker"
TZ = ZoneInfo("Europe/Lisbon")  # change if "today" should follow another timezone

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DATA_DIR / "config.json"
PHOTO_FILES = {"leonie": DATA_DIR / "leonie.jpg", "ko": DATA_DIR / "ko.jpg"}

INK = "#4a3b47"
RED = "#8f1d2c"

st.set_page_config(page_title=APP_TITLE, page_icon="❤️", layout="centered")

# Keep the Streamlit page itself clean, white and quiet
st.markdown(
    """
    <style>
    .stApp { background: #ffffff; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 760px; padding-top: 1.5rem; }
    [data-testid="stExpander"] summary p,
    [data-testid="stDateInput"] label p,
    [data-testid="stExpander"] p strong,
    [data-testid="stFileUploader"] label p,
    [data-testid="stExpander"] summary svg { color: #8f1d2c !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Persistence
# ----------------------------------------------------------------------------
def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def save_photo(uploaded_file, path: Path):
    """Crop the upload to a square and store it as a small JPEG."""
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img = ImageOps.fit(img, (400, 400), centering=(0.5, 0.4))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    path.write_bytes(buf.getvalue())


def photo_uri(path: Path):
    if not path.exists():
        return None
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


# ----------------------------------------------------------------------------
# Drawing
# ----------------------------------------------------------------------------
def head_svg(kind: str, uri):
    """Head centred at (0, 110), radius 46. Uses the photo if there is one."""
    if uri:
        return f"""
        <clipPath id="clip-{kind}"><circle cx="0" cy="110" r="46"/></clipPath>
        <image href="{uri}" x="-46" y="64" width="92" height="92"
               clip-path="url(#clip-{kind})" preserveAspectRatio="xMidYMid slice"/>
        <circle cx="0" cy="110" r="46" fill="none" stroke="{INK}" stroke-width="3.5"/>
        """
    hair_color = "#8b5a3c" if kind == "girl" else "#6b4a35"
    hair = (
        "M-47 112 C-52 56 52 56 47 112 C40 90 20 78 0 78 C-20 78 -40 90 -47 112 Z"
        if kind == "girl"
        else "M-46 104 C-48 62 48 62 46 104 C36 84 20 80 0 84 C-20 80 -36 84 -46 104 Z"
    )
    return f"""
    <circle cx="0" cy="110" r="46" fill="#ffe3cf" stroke="{INK}" stroke-width="3.5"/>
    <path d="{hair}" fill="{hair_color}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
    <circle cx="-16" cy="114" r="4" fill="{INK}"/><circle cx="16" cy="114" r="4" fill="{INK}"/>
    <ellipse cx="-27" cy="126" rx="7" ry="4" fill="#ffb3c6" opacity=".8"/>
    <ellipse cx="27" cy="126" rx="7" ry="4" fill="#ffb3c6" opacity=".8"/>
    <path d="M-11 129 Q0 141 11 129" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
    """


def girl_svg(x, uri, still):
    return f"""
    <g transform="translate({x:.1f} 0)">
      <g class="bob {'still' if still else ''}">
        <g stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none">
          <path d="M-12 252 L-14 288 M12 252 L14 288"/>
          <ellipse cx="-17" cy="291" rx="10" ry="5" fill="{RED}"/>
          <ellipse cx="17" cy="291" rx="10" ry="5" fill="{RED}"/>
          <path d="M-9 176 Q-26 205 -30 232"/>
          <path d="M9 176 Q42 190 60 215"/>
          <path d="M0 158 L-36 254 Q0 266 36 254 Z" fill="#ffd1dc"/>
          <circle cx="-30" cy="234" r="6" fill="#ffe3cf"/>
          <circle cx="60" cy="215" r="7" fill="#ffe3cf"/>
        </g>
        {head_svg("girl", uri)}
        <g transform="translate(-28 68) rotate(-20)" fill="{RED}" stroke="{INK}" stroke-width="2" stroke-linejoin="round">
          <path d="M0 0 L-15 -10 L-15 10 Z"/><path d="M0 0 L15 -10 L15 10 Z"/>
          <circle r="4.5"/>
        </g>
        <text y="322" text-anchor="middle" class="name">Leonie</text>
      </g>
    </g>
    """


def boy_svg(x, uri, still):
    return f"""
    <g transform="translate({x:.1f} 0)">
      <g class="bob b2 {'still' if still else ''}">
        <g stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none">
          <path d="M-10 236 L-12 288 M10 236 L12 288"/>
          <ellipse cx="-15" cy="291" rx="10" ry="5" fill="#7fa6d1"/>
          <ellipse cx="15" cy="291" rx="10" ry="5" fill="#7fa6d1"/>
          <path d="M20 176 Q30 205 30 232"/>
          <path d="M-20 176 Q-42 190 -60 215"/>
          <rect x="-22" y="158" width="44" height="80" rx="12" fill="#cfe8ff"/>
          <circle cx="30" cy="234" r="6" fill="#ffe3cf"/>
          <circle cx="-60" cy="215" r="7" fill="#ffe3cf"/>
        </g>
        <text x="0" y="206" text-anchor="middle" font-size="20" fill="{RED}">♥</text>
        {head_svg("boy", uri)}
        <text y="322" text-anchor="middle" class="name">Ko</text>
      </g>
    </g>
    """


def scene_svg(progress, reunited, girl_uri, boy_uri):
    girl_x = 90 + 250 * progress  # ends at 340
    boy_x = 710 - 250 * progress  # ends at 460 -> hands meet at x = 400
    floating = ""
    if reunited:
        floating = "".join(
            f'<text class="fh" x="{x}" y="175" style="animation-delay:{d}s" '
            f'font-size="{s}" fill="{RED}" text-anchor="middle">♥</text>'
            for x, d, s in [(380, 0, 22), (400, 0.9, 30), (420, 1.8, 22)]
        )
    return f"""
    <svg viewBox="0 0 800 335" class="scene" role="img"
         aria-label="Leonie and Ko walking towards each other">
      <path d="M20 296 L780 296" stroke="#f7c6d3" stroke-width="4"
            stroke-dasharray="2 12" stroke-linecap="round"/>
      {girl_svg(girl_x, girl_uri, reunited)}
      {boy_svg(boy_x, boy_uri, reunited)}
      {floating}
    </svg>
    """


PAGE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
<style>
  html, body { margin: 0; background: #ffffff; }
  body {
    font-family: "Quicksand", "Trebuchet MS", sans-serif;
    color: __INK__; text-align: center; padding: 8px 12px 24px;
  }
  .brand { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 6px; }
  .brand svg { width: 34px; height: 31px; }
  h1 {
    font-family: "Pacifico", "Brush Script MT", cursive; font-weight: 400;
    font-size: clamp(26px, 6vw, 40px); margin: 0; color: __RED__; line-height: 1.2;
  }
  .sub { margin: 2px 0 26px; font-weight: 700; letter-spacing: .04em; color: #b08a98; font-size: 15px; }

  .heart-wrap {
    position: relative; width: min(340px, 78vw); margin: 0 auto;
    animation: beat 1.4s ease-in-out infinite; transform-origin: 50% 55%;
  }
  .heart { width: 100%; display: block; overflow: visible; filter: drop-shadow(0 8px 16px rgba(224,36,94,.22)); }
  .heart path { fill: #fff6f8; stroke: __RED__; stroke-width: 2.6; stroke-linejoin: round; }
  .count {
    position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; padding-bottom: 9%;
  }
  .num { font-family: "Pacifico", cursive; color: __RED__; line-height: 1; font-size: clamp(54px, 17vw, 96px); }
  .num.small { font-size: clamp(32px, 10vw, 54px); }
  .lbl { font-weight: 700; margin-top: 6px; font-size: clamp(14px, 3.6vw, 18px); color: __INK__; }
  @keyframes beat {
    0%, 70%, 100% { transform: scale(1); }
    14% { transform: scale(1.07); }
    28% { transform: scale(1); }
    42% { transform: scale(1.1); }
  }

  .date { margin-top: 26px; font-weight: 700; font-size: clamp(15px, 3.8vw, 19px); }
  .progress { margin-top: 2px; font-size: 14px; color: #b08a98; font-weight: 500; }

  .scene { width: min(720px, 100%); height: auto; margin-top: 22px; overflow: visible; }
  .name { font-family: "Pacifico", cursive; font-size: 20px; fill: __INK__; }
  .bob { animation: bob 1s ease-in-out infinite; }
  .bob.b2 { animation-delay: .5s; }
  .bob.still { animation: none; }
  @keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
  .fh { opacity: 0; animation: floatup 2.7s ease-out infinite; }
  @keyframes floatup {
    0% { transform: translateY(0); opacity: 0; }
    20% { opacity: 1; }
    100% { transform: translateY(-80px); opacity: 0; }
  }
  @media (prefers-reduced-motion: reduce) {
    .heart-wrap, .bob, .fh { animation: none; }
    .fh { opacity: 1; }
  }
  @media (max-width: 480px) {
    body { padding: 4px 8px 18px; }
    .brand { gap: 8px; margin-top: 2px; }
    .brand svg { width: 28px; height: 25px; }
    h1 { font-size: clamp(24px, 8.5vw, 32px); }
    .sub { margin-bottom: 14px; font-size: 13px; }
    .heart-wrap { width: min(280px, 78vw); }
    .date { margin-top: 18px; font-size: 15px; }
    .progress { padding: 0 4px; font-size: 13px; }
    .scene { margin-top: 14px; }
    .name { font-size: 18px; }
  }
</style>
</head>
<body>
  <div class="brand">
    <svg viewBox="0 0 100 90" aria-hidden="true"><path d="__HEART__" fill="__RED__"/></svg>
    <h1>Leonie &amp; Ko</h1>
  </div>
  <div class="sub">Reunion Tracker</div>

  <div class="heart-wrap">
    <svg class="heart" viewBox="0 0 100 90" aria-hidden="true"><path d="__HEART__"/></svg>
    <div class="count">
      <div class="num __NUMCLASS__">__NUM__</div>
      <div class="lbl">__LABEL__</div>
    </div>
  </div>

  <div class="date">__DATE__</div>
  <div class="progress">__PROGRESS__</div>

  __SCENE__
</body>
</html>
"""

HEART_PATH = (
    "M50 86 C20 62 3 45 3 27 C3 13 14 4 27 4 C37 4 45 10 50 19 "
    "C55 10 63 4 73 4 C86 4 97 13 97 27 C97 45 80 62 50 86 Z"
)


def render_page(reunion: date, start: date, today: date, girl_uri, boy_uri):
    remaining = (reunion - today).days
    total = max((reunion - start).days, 1)
    reunited = remaining <= 0
    progress = 1.0 if reunited else min(max(1 - remaining / total, 0.0), 1.0)

    if remaining > 0:
        num, num_class = str(remaining), ""
        label = "day to go" if remaining == 1 else "days to go"
        tagline = f"{round(progress * 100)}% of the way. A little closer every day."
    elif remaining == 0:
        num, num_class, label = "Today!", "small", "we are together"
        tagline = "Hand in hand at last."
    else:
        num, num_class, label = "Together", "small", "reunited"
        tagline = f"Reunited for {-remaining} day{'s' if remaining != -1 else ''}."

    html = (
        PAGE.replace("__INK__", INK)
        .replace("__RED__", RED)
        .replace("__HEART__", HEART_PATH)
        .replace("__NUMCLASS__", num_class)
        .replace("__NUM__", num)
        .replace("__LABEL__", label)
        .replace("__DATE__", reunion.strftime("%A, %d %B %Y"))
        .replace("__PROGRESS__", tagline)
        .replace("__SCENE__", scene_svg(progress, reunited, girl_uri, boy_uri))
    )
    components.html(html, height=840, scrolling=False)


# ----------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------
today = datetime.now(TZ).date()

cfg = load_config()
first_run = cfg is None
if first_run:
    cfg = {
        "reunion": (today + timedelta(days=30)).isoformat(),
        "start": today.isoformat(),
    }
    save_config(cfg)

st.session_state.setdefault("uploader_version", 0)
ver = st.session_state["uploader_version"]

with st.expander("Settings", expanded=True):
    new_reunion = st.date_input(
        "Reunion date",
        value=date.fromisoformat(cfg["reunion"]),
        format="DD.MM.YYYY",
    )
    new_start = st.date_input(
        "Countdown started on",
        value=date.fromisoformat(cfg["start"]),
        format="DD.MM.YYYY",
        help="The day you two walk off from. It sets how far apart the figures start.",
    )
    if new_reunion.isoformat() != cfg["reunion"] or new_start.isoformat() != cfg["start"]:
        cfg["reunion"] = new_reunion.isoformat()
        cfg["start"] = new_start.isoformat()
        save_config(cfg)

    st.markdown("**Photos for the heads**")
    cols = st.columns(2)
    for col, key, name in zip(cols, ["leonie", "ko"], ["Leonie", "Ko"]):
        with col:
            upload = st.file_uploader(
                f"{name}'s photo",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"upload_{key}_{ver}",
            )
            if upload is not None:
                save_photo(upload, PHOTO_FILES[key])
            if PHOTO_FILES[key].exists() and st.button(f"Remove {name}'s photo", key=f"rm_{key}_{ver}"):
                PHOTO_FILES[key].unlink()
                st.session_state["uploader_version"] += 1
                st.rerun()
    st.caption("Everything is saved automatically and stays until you change it.")

visual = st.container()
with visual:
    render_page(
        reunion=date.fromisoformat(cfg["reunion"]),
        start=date.fromisoformat(cfg["start"]),
        today=today,
        girl_uri=photo_uri(PHOTO_FILES["leonie"]),
        boy_uri=photo_uri(PHOTO_FILES["ko"]),
    )
