import streamlit as st
import ollama
from PIL import Image, ImageDraw
import subprocess
import tempfile
import os
import numpy as np
import base64
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

def _load_env_file(filepath=".env"):
    """Load variables from .env file into os.environ."""
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    env_path = os.path.join(base_dir, filepath)
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    if key and val:
                        os.environ[key] = val
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    load_dotenv(os.path.join(base_dir, ".env"), override=True)
except ImportError:
    pass

_load_env_file()

try:
    if ("ELEVENLABS_API_KEY" not in os.environ or not os.environ["ELEVENLABS_API_KEY"]) and hasattr(st, "secrets") and "ELEVENLABS_API_KEY" in st.secrets:
        os.environ["ELEVENLABS_API_KEY"] = st.secrets["ELEVENLABS_API_KEY"]
except Exception:
    pass

with open("bg.jpeg", "rb") as f:
    bg_image = base64.b64encode(f.read()).decode()
st.markdown("""
<style>

/* =========================================================
   CETACEAN INTERFACE — ORGANIC BLOBBLET / Y2K DEVICE SKIN
   ========================================================= */


/* ---------- OCEAN BACKGROUND ---------- */

.stApp {
    background-image: url("data:image/jpeg;base64,__BG_IMAGE__");
    background-position: center;
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;

    min-height: 100vh;
}


/* ---------- MAIN ORGANIC DEVICE BODY ---------- */

.block-container {
    max-width: 1180px;

    padding: 3.5rem 3.5rem 3rem 3.5rem;

    margin: 8vh auto;
    width: 760px;
    max-width: calc(100vw - 80px);

    background:
        radial-gradient(
            ellipse at 25% 8%,
            rgba(255,255,255,1),
            rgba(255,255,255,0) 35%
        ),
        radial-gradient(
            ellipse at 80% 85%,
            rgba(190,220,255,0.7),
            rgba(190,220,255,0) 45%
        ),
        linear-gradient(
            145deg,
            #ffffff 0%,
            #edf4ff 42%,
            #c9daf6 100%
        );

    border: none;

    /*
       Huge radius makes this read as molded plastic,
       NOT as a normal webpage card.
    */
    border-radius: 500px 500px 500px 500px;

    box-shadow:
        0 35px 65px rgba(45,75,145,0.32),
        inset 0 5px 12px rgba(255,255,255,1),
        inset 0 -12px 25px rgba(80,120,200,0.18);

}


/* ---------- TITLES ---------- */

h1, h2, h3 {
    color: #164c99 !important;
    text-align: center !important;
}

h1 {
    font-weight: 850 !important;
    letter-spacing: -2px;

    text-shadow:
        0 2px 0 rgba(255,255,255,0.95),
        0 4px 10px rgba(55,100,180,0.18);
}

h2, h3 {
    font-weight: 800 !important;

    text-shadow:
        0 2px 0 rgba(255,255,255,0.9),
        0 3px 7px rgba(55,100,180,0.15);
}

/* ---------- SUBHEADINGS AS ORGANIC LABELS ---------- */

.stSubheader {
    color: #164c99 !important;

    font-weight: 800 !important;

    letter-spacing: 0.5px;
}


/* ---------- UPLOAD BLOBS ---------- */

[data-testid="stFileUploader"] {

    background:
        radial-gradient(
            ellipse at 25% 15%,
            rgba(255,255,255,1),
            rgba(255,255,255,0) 45%
        ),
        linear-gradient(
            145deg,
            #fafdff 0%,
            #dcecff 50%,
            #a9c9ef 100%
        ) !important;

    border: 1px solid rgba(255,255,255,0.98) !important;

    border-radius:
        65px
        45px
        75px
        55px !important;

    padding: 15px !important;

    box-shadow:
        0 12px 25px rgba(50,90,160,0.25),
        inset 0 4px 8px rgba(255,255,255,1),
        inset 0 -7px 14px rgba(60,110,190,0.18) !important;
}


/* ---------- INNER UPLOAD WELL ---------- */

[data-testid="stFileUploader"] section {

    background:
        radial-gradient(
            ellipse at 30% 20%,
            rgba(255,255,255,0.95),
            rgba(255,255,255,0) 45%
        ),
        linear-gradient(
            145deg,
            #eaf5ff,
            #c5def8
        ) !important;

    border: 1px solid rgba(255,255,255,0.9) !important;

    border-radius:
        50px
        35px
        60px
        42px !important;

    box-shadow:
        inset 0 3px 7px rgba(255,255,255,1),
        inset 0 -5px 12px rgba(65,110,180,0.15) !important;
}


/* ---------- UPLOAD TEXT ---------- */

[data-testid="stFileUploader"] label {
    color: #174d9b !important;
}

[data-testid="stFileUploader"] section p {
    color: #244d7d !important;
}

[data-testid="stFileUploader"] section small {
    color: #5b78a0 !important;
}


/* ---------- BROWSE BUTTON = LITTLE PLASTIC BLOB ---------- */

[data-testid="stFileUploader"] button {

    border-radius: 999px !important;

    border: 0px solid rgba(255,255,255,0.98) !important;

    background:
        radial-gradient(
            ellipse at 30% 20%,
            #ffffff,
            transparent 45%
        ),
        linear-gradient(
            145deg,
            #ffffff,
            #c8e2ff 55%,
            #79aaf0
        ) !important;

    color: #164c99 !important;

    font-weight: 800 !important;

    box-shadow:
        0 7px 13px rgba(50,90,160,0.28),
        inset 0 3px 6px rgba(255,255,255,1),
        inset 0 -5px 8px rgba(50,100,190,0.2) !important;
}


/* ---------- ALL OTHER BUTTONS ---------- */

[data-testid="stButton"],
.stButton,
div[data-testid="stElementContainer"]:has(.stButton),
div[data-testid="stElementContainer"]:has([data-testid="stButton"]) {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stButton"] > button,
.stButton > button,
button[data-testid^="stBaseButton"] {
    margin: 0 auto !important;
    display: block !important;

    min-height: 64px;
    width: 100% !important;
    max-width: 380px !important;

    border-radius: 999px !important;

    border: 0px solid rgba(255,255,255,0.98) !important;

    background:
        radial-gradient(
            ellipse at 30% 15%,
            #ffffff 0%,
            rgba(255,255,255,0) 42%
        ),
        linear-gradient(
            145deg,
            #dff2ff 0%,
            #7bb6f4 48%,
            #236fd1 100%
        ) !important;

    color: #ffffff !important;

    font-weight: 850 !important;

    letter-spacing: 0.5px;

    box-shadow:
        0 10px 18px rgba(35,85,160,0.35),
        inset 0 4px 7px rgba(255,255,255,0.95),
        inset 0 -7px 12px rgba(20,70,160,0.3) !important;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}


/* ---------- BUTTON HOVER ---------- */

.stButton > button:hover {

    transform: translateY(-3px);

    box-shadow:
        0 14px 22px rgba(35,85,160,0.4),
        inset 0 4px 8px rgba(255,255,255,1),
        inset 0 -7px 12px rgba(20,70,160,0.28) !important;
}


/* ---------- BUTTON PRESS ---------- */

.stButton > button:active {

    transform: translateY(3px);

    box-shadow:
        inset 0 6px 12px rgba(20,70,150,0.35),
        0 3px 6px rgba(40,80,150,0.2) !important;
}


/* ---------- AUDIO PLAYER ---------- */

audio {

    width: 100%;

    border-radius: 999px;

    box-shadow:
        0 7px 15px rgba(45,85,150,0.2),
        inset 0 2px 5px rgba(255,255,255,0.9);
}


/* ---------- STATUS / WARNING BLOBS ---------- */

[data-testid="stAlert"] {

    border-radius:
        45px
        32px
        55px
        38px !important;

    border: 1px solid rgba(255,255,255,0.95) !important;

    background:
        radial-gradient(
            ellipse at 25% 15%,
            rgba(255,255,255,0.95),
            rgba(255,255,255,0) 50%
        ),
        linear-gradient(
            145deg,
            #eaf6ff,
            #b9d7f5
        ) !important;

    box-shadow:
        0 9px 18px rgba(50,90,150,0.22),
        inset 0 3px 7px rgba(255,255,255,1),
        inset 0 -6px 12px rgba(70,110,180,0.16) !important;
}


/* ---------- IMAGE = ORGANIC SCREEN ---------- */

[data-testid="stImage"] {

    padding: 10px;

    background:
        linear-gradient(
            145deg,
            #ffffff,
            #b7d6f7
        );

    border-radius:
        70px
        45px
        80px
        55px;

    box-shadow:
        0 15px 28px rgba(40,80,150,0.3),
        inset 0 4px 8px rgba(255,255,255,1),
        inset 0 -8px 15px rgba(60,110,190,0.18);
}


[data-testid="stImage"] img {

    border-radius:
        55px
        38px
        65px
        45px;

    border: 4px solid rgba(255,255,255,0.85);

    box-shadow:
        inset 0 3px 8px rgba(255,255,255,0.6);
}


/* ---------- GENERAL TEXT & BLUE BODY TEXT ---------- */

html, body, [class*="css"], .stApp, .block-container {
    color: #164c99 !important;
}

p, span, label, li, small, div, strong, em {
    color: #164c99 !important;
    text-align: center !important;
}

.stMarkdown, .stMarkdown * {
    color: #164c99 !important;
    text-align: center !important;
}

/* Small device-like metadata & captions */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
[data-testid="stImageCaption"], figcaption, .stCaption {
    color: #164c99 !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    text-align: center !important;
}

/* Metric styling in blue */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #f0f7ff, #d2e4fb) !important;
    padding: 12px 15px !important;
    border-radius: 30px !important;
    border: 1px solid rgba(255,255,255,0.95) !important;
    box-shadow: inset 0 2px 5px rgba(255,255,255,0.85), 0 6px 14px rgba(45,75,145,0.12) !important;
    text-align: center !important;
}

[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
    color: #164c99 !important;
    font-weight: 800 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
    justify-content: center !important;
    text-align: center !important;
}

[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color: #103d7e !important;
    font-weight: 850 !important;
    font-size: 1.35rem !important;
    text-align: center !important;
}

/* File uploader labels and body text */
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] label * {
    color: #164c99 !important;
    font-weight: 700 !important;
}

[data-testid="stFileUploader"] section p,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section div {
    color: #244d7d !important;
}

[data-testid="stFileUploader"] section small {
    color: #4b74a6 !important;
}


/* ---------- REMOVE STREAMLIT CHROME ---------- */

header {
    background: transparent !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ---------- EXTRA ORGANIC DEPTH ---------- */

hr {
    border: none !important;

    height: 14px;

    background:
        radial-gradient(
            ellipse,
            rgba(120,165,220,0.18),
            transparent 70%
        );

    margin: 25px 0;
}

/* ---------- CENTER-ALIGNED INTERPRETATION ELEMENTS & BLUE SPINNER ---------- */

/* Spinner Container & Centered Text */
[data-testid="stSpinner"],
.stSpinner,
div[data-testid="stElementContainer"]:has([data-testid="stSpinner"]),
div[data-testid="stElementContainer"]:has(.stSpinner) {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    width: 100% !important;
    margin: 1.5rem auto !important;
}

[data-testid="stSpinner"] > div,
.stSpinner > div {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    margin: 0 auto !important;
}

/* Spinner Text: "DECODING CETACEAN TRANSMISSION..." */
[data-testid="stSpinner"] span,
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] div,
.stSpinner span,
.stSpinner p {
    text-align: center !important;
    color: #164c99 !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}

/* Spinner Circle — Vibrant Aqua / Blue */
[data-testid="stSpinner"] svg,
.stSpinner svg {
    stroke: #1e70d6 !important;
    color: #1e70d6 !important;
    fill: none !important;
}

[data-testid="stSpinner"] svg circle,
[data-testid="stSpinner"] svg path,
.stSpinner svg circle,
.stSpinner svg path {
    stroke: #1e70d6 !important;
    color: #1e70d6 !important;
}

[data-testid="stSpinner"] [data-testid="stSpinnerIcon"],
[data-testid="stSpinner"] i,
.stSpinner i,
.stSpinner [data-testid="stSpinnerIcon"],
[data-testid="stSpinner"] > div > div:first-child,
.stSpinner > div > div:first-child {
    border-top-color: #1e70d6 !important;
    border-right-color: rgba(30, 112, 214, 0.2) !important;
    border-bottom-color: rgba(30, 112, 214, 0.2) !important;
    border-left-color: rgba(30, 112, 214, 0.2) !important;
    color: #1e70d6 !important;
}

/* Session Status Text Centered */
.session-status-block {
    text-align: center !important;
    margin: 0.4rem auto 1.2rem auto !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}

.status-item {
    text-align: center !important;
    color: #164c99 !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px !important;
    margin: 2px 0 !important;
    width: 100% !important;
}

/* ElevenLabs / API Key Settings Centered */
[data-testid="stExpander"],
.streamlit-expanderContent {
    text-align: center !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stExpander"] summary {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
}

[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary div {
    text-align: center !important;
    color: #164c99 !important;
    font-weight: 800 !important;
}

[data-testid="stExpander"] [data-testid="stAlert"] {
    text-align: center !important;
    justify-content: center !important;
    display: flex !important;
    align-items: center !important;
}

[data-testid="stExpander"] [data-testid="stAlert"] * {
    text-align: center !important;
    justify-content: center !important;
}

[data-testid="stExpander"] label,
[data-testid="stExpander"] label p,
[data-testid="stExpander"] label span {
    text-align: center !important;
    width: 100% !important;
    display: block !important;
    justify-content: center !important;
    font-weight: 700 !important;
    color: #164c99 !important;
}

[data-testid="stExpander"] [data-baseweb="input"] {
    margin: 0 auto !important;
    max-width: 380px !important;
}

[data-testid="stExpander"] input {
    text-align: center !important;
}

[data-testid="stExpander"] .stCaption,
[data-testid="stExpander"] small,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {
    text-align: center !important;
}

[data-testid="stExpander"] [data-testid="stButton"],
[data-testid="stExpander"] .stButton {
    display: flex !important;
    justify-content: center !important;
    margin: 8px auto !important;
}

[data-testid="stExpander"] .stButton > button {
    max-width: 260px !important;
    min-height: 48px !important;
    font-size: 0.9rem !important;
    margin: 0 auto !important;
}

</style>
""".replace("__BG_IMAGE__", bg_image), unsafe_allow_html=True)
if "interpretation" not in st.session_state:
    st.session_state.interpretation = None
if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None

def get_speech_length_guideline(duration_s):
    if duration_s < 2.0:
        return "1 to 4 words (e.g. 'Easy, pal.', 'Beat it.')"
    elif duration_s < 3.0:
        return "3 to 7 words (e.g. 'Easy there, pal.', 'Watch where you swim.')"
    elif duration_s < 5.0:
        return "6 to 12 words (e.g. 'Keep it moving buddy, these waters belong to us.')"
    elif duration_s < 8.0:
        return "10 to 20 words"
    elif duration_s < 12.0:
        return "18 to 30 words"
    else:
        return "concise, no more than 35 words"

# =========================================================
# ELEVENLABS PREDEFINED APPROVED VOICE IDS
# Add or modify approved ElevenLabs Voice IDs below.
# Each TTS generation will randomly pick one from this list.
# =========================================================
import random

ELEVENLABS_VOICE_IDS = [
    "pNInz6obpgDQGcFmaJgB",  
    "JBFqnCBsd6RMkjVDRZzb",  
    "ErXwobaYiN019PkySvjV",  
    "QyX5mnB5hVBPeNS1oyvU",
    "QzTKubutNn9TjrB7Xb2Q",
    "j9qIyycr9PcZ7d4yj21f",
    "M9UAxraM2w5tCjpOaIB0",
    "lAqElvydqyTzitpwAdj6",
    "INDKfphIpZiLCUiXae4o",
    "KUqzTMhYFYqnFWfMUjfX",
]

def get_random_elevenlabs_voice_id():
    """Randomly choose one Voice ID from ELEVENLABS_VOICE_IDS with graceful fallback."""
    valid_voices = [v.strip() for v in ELEVENLABS_VOICE_IDS if isinstance(v, str) and v.strip()]
    if valid_voices:
        return random.choice(valid_voices)
    # Graceful fallback if list is empty or unconfigured
    return os.environ.get("ELEVENLABS_VOICE_ID", "").strip() or "pNInz6obpgDQGcFmaJgB"

def generate_tts_audio(text):
    if not text or not text.strip():
        return None
    clean_text = text.strip('"\'\n\r ')

    # 1. ElevenLabs TTS (if ELEVENLABS_API_KEY environment variable is configured)
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if api_key:
        try:
            import requests
            voice_id = get_random_elevenlabs_voice_id()
            model_id = os.environ.get("ELEVENLABS_MODEL_ID", "").strip() or "eleven_multilingual_v2"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key,
            }
            payload = {
                "text": clean_text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                },
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=12)
            if resp.status_code == 200 and resp.content:
                return resp.content
        except Exception:
            # Fall back to local synthesis without exposing credentials or details in logs
            pass

    # 2. Native macOS say command (offline, fast, zero-dependency)
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            wav_path = temp_wav.name
        cmd = ["say", "-o", wav_path, "--data-format=LEI16@22050", clean_text]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
        if res.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            with open(wav_path, "rb") as f:
                data = f.read()
            try:
                os.remove(wav_path)
            except OSError:
                pass
            return data
    except Exception:
        pass

    # 3. Fallback to gTTS if available
    try:
        from gtts import gTTS
        import io
        tts = gTTS(text=clean_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        pass

    return None

generate_translation_audio = generate_tts_audio

def extract_transmission_dialogue(full_text):
    if not full_text:
        return ""
    lines = full_text.split("\n")
    found_header = False
    for line in lines:
        if "TRANSLATED TRANSMISSION" in line.upper():
            found_header = True
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                return parts[1].strip().strip('"\'')
            continue
        if found_header:
            s = line.strip()
            if s:
                return s.strip('"\'')
    import re
    quotes = re.findall(r'["\']([^"\']{2,120})["\']', full_text)
    if quotes:
        return quotes[-1].strip()
    return full_text.strip().split("\n")[-1].strip('"\'')

def render_frutiger_audio_player(audio_bytes):
    b64_audio = base64.b64encode(audio_bytes).decode()
    if audio_bytes.startswith(b"RIFF"):
        mime_type = "audio/wav"
    elif audio_bytes.startswith(b"ID3") or (len(audio_bytes) > 2 and audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        mime_type = "audio/mpeg"
    elif audio_bytes.startswith(b"OggS"):
        mime_type = "audio/ogg"
    else:
        mime_type = "audio/mpeg"
    player_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: transparent;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 6px 0;
    }}
    .frutiger-pod {{
      width: 100%;
      max-width: 580px;
      background:
        radial-gradient(ellipse at 30% 8%, rgba(255,255,255,0.98), rgba(255,255,255,0.45) 40%, rgba(205,235,255,0.7) 75%),
        linear-gradient(155deg, rgba(245,252,255,0.95) 0%, rgba(195,228,255,0.85) 50%, rgba(145,198,245,0.9) 100%);
      border-radius: 42px 58px 45px 52px;
      border: 2px solid rgba(255,255,255,0.95);
      box-shadow:
        0 18px 36px rgba(35,80,150,0.22),
        inset 0 3px 7px rgba(255,255,255,0.95),
        inset 0 -8px 16px rgba(40,100,190,0.18);
      padding: 16px 22px 14px 22px;
      position: relative;
      overflow: hidden;
    }}
    .frutiger-pod::before {{
      content: "";
      position: absolute;
      top: 0; left: 12%; right: 12%;
      height: 16px;
      background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0) 100%);
      border-radius: 0 0 50% 50%;
      pointer-events: none;
    }}
    .player-header {{
      text-align: center;
      margin-bottom: 8px;
    }}
    .player-title {{
      color: #104080;
      font-size: 13px;
      font-weight: 850;
      letter-spacing: 0.8px;
      text-shadow: 0 1px 0 rgba(255,255,255,0.9);
    }}
    .player-sub {{
      color: #386ba8;
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 1px;
      margin-top: 1px;
    }}
    .screen-wrapper {{
      background: #06162a;
      border-radius: 16px;
      border: 2px solid rgba(255,255,255,0.85);
      box-shadow: inset 0 4px 10px rgba(0,0,0,0.6), 0 3px 6px rgba(30,70,140,0.15);
      padding: 6px 8px;
      position: relative;
      overflow: hidden;
      margin-bottom: 10px;
    }}
    .screen-wrapper::after {{
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 45%;
      background: linear-gradient(180deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 100%);
      border-radius: 14px 14px 40% 40%;
      pointer-events: none;
    }}
    canvas {{
      width: 100%;
      height: 64px;
      display: block;
    }}
    .controls-row {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 6px;
    }}
    .play-btn {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 2px solid rgba(255,255,255,0.95);
      background: radial-gradient(circle at 35% 25%, #ffffff 0%, #6ec2ff 45%, #186edb 80%, #0c438c 100%);
      box-shadow: 0 5px 12px rgba(20,70,150,0.32), inset 0 2px 4px rgba(255,255,255,0.9), inset 0 -3px 6px rgba(0,30,80,0.4);
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-shrink: 0;
      outline: none;
      transition: transform 0.1s, box-shadow 0.1s;
    }}
    .play-btn:hover {{
      transform: scale(1.05);
      box-shadow: 0 7px 16px rgba(20,70,150,0.42), inset 0 2px 5px rgba(255,255,255,1);
    }}
    .play-btn:active {{
      transform: scale(0.96);
      box-shadow: inset 0 3px 6px rgba(0,30,80,0.5), 0 2px 4px rgba(20,70,150,0.2);
    }}
    .play-icon {{
      width: 16px;
      height: 16px;
      fill: #ffffff;
      filter: drop-shadow(0 1px 1px rgba(0,20,60,0.4));
    }}
    .progress-container {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .progress-track {{
      height: 10px;
      background: rgba(185,215,245,0.65);
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.9);
      box-shadow: inset 0 2px 4px rgba(20,60,130,0.2);
      position: relative;
      cursor: pointer;
      overflow: hidden;
    }}
    .progress-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #4dd5ff, #0084ff);
      border-radius: 999px;
      position: relative;
      transition: width 0.05s linear;
    }}
    .progress-fill::after {{
      content: "";
      position: absolute;
      top: 1px; left: 2px; right: 2px; height: 3px;
      background: rgba(255,255,255,0.75);
      border-radius: 999px;
    }}
    .time-row {{
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: #104080;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .volume-group {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }}
    .vol-icon {{
      width: 13px;
      height: 13px;
      fill: #225a9c;
    }}
    .vol-slider {{
      width: 50px;
      -webkit-appearance: none;
      background: rgba(185,215,245,0.65);
      height: 6px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.9);
      outline: none;
    }}
    .vol-slider::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 30%, #ffffff, #2a88f5);
      border: 1px solid #ffffff;
      cursor: pointer;
      box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }}
    .footer-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 9.5px;
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px solid rgba(255,255,255,0.7);
    }}
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-weight: 800;
      color: #104080;
      letter-spacing: 0.5px;
    }}
    .status-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #a0c4e8;
      box-shadow: 0 0 5px #a0c4e8;
      display: inline-block;
    }}
    .status-dot.playing {{
      background: #00e676;
      box-shadow: 0 0 8px #00e676;
    }}
    .status-dot.complete {{
      background: #2979ff;
      box-shadow: 0 0 6px #2979ff;
    }}
    .meta-text {{
      color: #3b6ea8;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    </style>
    </head>
    <body>
    <div class="frutiger-pod">
      <div class="player-header">
        <div class="player-title">INTERPRETED TRANSMISSION</div>
        <div class="player-sub">AUDIO PLAYBACK • LOCAL SYNTHESIS</div>
      </div>
      <div class="screen-wrapper">
        <canvas id="visCanvas"></canvas>
      </div>
      <div class="controls-row">
        <button class="play-btn" id="playBtn" title="Play / Pause">
          <svg class="play-icon" id="playIcon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        </button>
        <div class="progress-container">
          <div class="progress-track" id="progressTrack">
            <div class="progress-fill" id="progressFill"></div>
          </div>
          <div class="time-row">
            <span id="currTime">0:00</span>
            <span id="durTime">0:00</span>
          </div>
        </div>
        <div class="volume-group">
          <svg class="vol-icon" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
          <input type="range" class="vol-slider" id="volSlider" min="0" max="1" step="0.05" value="1">
        </div>
      </div>
      <div class="footer-row">
        <div class="status-badge">
          <span class="status-dot" id="statusDot"></span>
          <span id="statusText">⚪ TRANSMISSION PAUSED</span>
        </div>
        <div class="meta-text">ID: CET-042 • FORMAT: AUDIO SYNTHESIS</div>
      </div>
    </div>

    <script>
    (function() {{
      const audio = new Audio("data:{mime_type};base64,{b64_audio}");
      const playBtn = document.getElementById("playBtn");
      const playIcon = document.getElementById("playIcon");
      const progressTrack = document.getElementById("progressTrack");
      const progressFill = document.getElementById("progressFill");
      const currTime = document.getElementById("currTime");
      const durTime = document.getElementById("durTime");
      const volSlider = document.getElementById("volSlider");
      const statusDot = document.getElementById("statusDot");
      const statusText = document.getElementById("statusText");
      const canvas = document.getElementById("visCanvas");
      const ctx = canvas.getContext("2d");

      let audioCtx = null;
      let analyser = null;
      let source = null;
      let dataArray = null;
      let bufferLength = 0;
      let animId = null;

      function resizeCanvas() {{
        canvas.width = canvas.parentElement.clientWidth * (window.devicePixelRatio || 1) || 500;
        canvas.height = canvas.parentElement.clientHeight * (window.devicePixelRatio || 1) || 64;
      }}
      window.addEventListener("resize", resizeCanvas);
      resizeCanvas();

      function initAudio() {{
        if (!audioCtx) {{
          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          audioCtx = new AudioContextClass();
          analyser = audioCtx.createAnalyser();
          analyser.fftSize = 128;
          analyser.smoothingTimeConstant = 0.8;
          bufferLength = analyser.frequencyBinCount;
          dataArray = new Uint8Array(bufferLength);
          source = audioCtx.createMediaElementSource(audio);
          source.connect(analyser);
          analyser.connect(audioCtx.destination);
        }}
        if (audioCtx.state === "suspended") {{
          audioCtx.resume();
        }}
      }}

      function formatTime(s) {{
        if (isNaN(s)) return "0:00";
        const m = Math.floor(s / 60);
        const sec = Math.floor(s % 60);
        return m + ":" + (sec < 10 ? "0" : "") + sec;
      }}

      audio.addEventListener("loadedmetadata", () => {{
        durTime.textContent = formatTime(audio.duration);
      }});

      audio.addEventListener("timeupdate", () => {{
        if (audio.duration) {{
          const pct = (audio.currentTime / audio.duration) * 100;
          progressFill.style.width = pct + "%";
          currTime.textContent = formatTime(audio.currentTime);
          durTime.textContent = formatTime(audio.duration);
        }}
      }});

      playBtn.addEventListener("click", () => {{
        initAudio();
        if (audio.paused) {{
          audio.play();
        }} else {{
          audio.pause();
        }}
      }});

      audio.addEventListener("play", () => {{
        statusDot.className = "status-dot playing";
        statusText.textContent = "🟢 PLAYING TRANSMISSION";
        playIcon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
        draw();
      }});

      audio.addEventListener("pause", () => {{
        if (audio.currentTime < audio.duration) {{
          statusDot.className = "status-dot";
          statusText.textContent = "⚪ TRANSMISSION PAUSED";
          playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
        }}
      }});

      audio.addEventListener("ended", () => {{
        statusDot.className = "status-dot complete";
        statusText.textContent = "🔵 TRANSMISSION COMPLETE";
        playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
        progressFill.style.width = "0%";
        currTime.textContent = "0:00";
      }});

      progressTrack.addEventListener("click", (e) => {{
        const rect = progressTrack.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        if (audio.duration) {{
          audio.currentTime = pos * audio.duration;
        }}
      }});

      volSlider.addEventListener("input", (e) => {{
        audio.volume = parseFloat(e.target.value);
      }});

      function draw() {{
        const w = canvas.width;
        const h = canvas.height;
        ctx.clearRect(0, 0, w, h);

        if (analyser && !audio.paused && !audio.ended) {{
          analyser.getByteFrequencyData(dataArray);
        }} else {{
          if (dataArray) dataArray.fill(3);
        }}

        // Draw frequency bars
        const barCount = 26;
        const barWidth = (w / barCount) * 0.72;
        const gap = (w / barCount) * 0.28;

        for (let i = 0; i < barCount; i++) {{
          const valIndex = Math.floor((i / barCount) * (bufferLength || 32));
          const val = dataArray ? dataArray[valIndex] : 3;
          const barHeight = Math.max(3, (val / 255) * (h * 0.72));
          const x = i * (barWidth + gap) + gap / 2;
          const y = h - barHeight;

          const grad = ctx.createLinearGradient(0, y, 0, h);
          grad.addColorStop(0, "#00f0ff");
          grad.addColorStop(0.5, "#0088ff");
          grad.addColorStop(1, "#03285c");

          ctx.fillStyle = grad;
          ctx.beginPath();
          if (ctx.roundRect) {{
            ctx.roundRect(x, y, barWidth, barHeight, [3, 3, 0, 0]);
          }} else {{
            ctx.rect(x, y, barWidth, barHeight);
          }}
          ctx.fill();
        }}

        // Draw glowing aqua waveform line over bars
        ctx.beginPath();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.8;
        ctx.shadowColor = "#00e5ff";
        ctx.shadowBlur = 6;

        const sliceWidth = w / (barCount - 1);
        let lx = 0;
        for (let i = 0; i < barCount; i++) {{
          const valIndex = Math.floor((i / barCount) * (bufferLength || 32));
          const val = dataArray ? dataArray[valIndex] : 0;
          const ly = h - Math.max(5, (val / 255) * (h * 0.82)) - 2;
          if (i === 0) ctx.moveTo(lx, ly);
          else ctx.lineTo(lx, ly);
          lx += sliceWidth;
        }}
        ctx.stroke();
        ctx.shadowBlur = 0;

        if (!audio.paused && !audio.ended) {{
          animId = requestAnimationFrame(draw);
        }}
      }}

      // Initial resting frame
      draw();
    }})();
    </script>
    </body>
    </html>
    """
    st.components.v1.html(player_html, height=245)

def analyze_audio(audio_file):
    audio_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
        temp.write(audio_file.read())
        input_path = temp.name

    output_path = input_path + ".wav"

    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    import wave

    with wave.open(output_path, "rb") as wav:
        frames = wav.readframes(wav.getnframes())
        sample_rate = wav.getframerate()

    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

    duration = len(samples) / sample_rate
    rms = np.sqrt(np.mean(samples ** 2))

    spectrum = np.abs(np.fft.rfft(samples))
    frequencies = np.fft.rfftfreq(len(samples), 1 / sample_rate)
    peak_frequency = frequencies[np.argmax(spectrum)]

    os.remove(input_path)
    os.remove(output_path)

    return {
        "duration_seconds": round(duration, 2),
        "average_amplitude": round(float(rms), 2),
        "dominant_frequency_hz": round(float(peak_frequency), 1),
        "samples": samples,
        "sample_rate": sample_rate
    }

def generate_signal_graph(samples, sample_rate):
    if len(samples) == 0:
        return None

    spectrum = np.abs(np.fft.rfft(samples))
    frequencies = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)

    if HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(7, 3), facecolor="none")
        ax.set_facecolor("#eaf4ff")

        ax.plot(frequencies, spectrum, color="#008cb4", linewidth=1.4, label="Frequency Contour")
        ax.fill_between(frequencies, spectrum, color="#79c5e8", alpha=0.35)

        ax.set_xlim(0, min(sample_rate / 2, 8000))
        ax.set_xlabel("Frequency (Hz)", color="#164c99", fontsize=9, fontweight="bold")
        ax.set_ylabel("Amplitude", color="#164c99", fontsize=9, fontweight="bold")
        ax.set_title("Frequency Contour & Spectrum", color="#164c99", fontsize=10, fontweight="bold")

        ax.tick_params(colors="#164c99", labelsize=8)
        ax.grid(True, color="#b8d8f8", linestyle="--", linewidth=0.6)

        for spine in ax.spines.values():
            spine.set_color("#79aaf0")
            spine.set_linewidth(1.0)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        return fig
    else:
        # High-definition PIL fallback if matplotlib is not installed in venv
        w, h = 640, 220
        img = Image.new("RGB", (w, h), color=(234, 244, 255))
        draw = ImageDraw.Draw(img)

        # Draw grid
        for x in range(50, w - 20, 70):
            draw.line([(x, 30), (x, h - 35)], fill=(184, 216, 248), width=1)
        for y in range(40, h - 35, 35):
            draw.line([(50, y), (w - 20, y)], fill=(184, 216, 248), width=1)

        # Plot contour
        max_f = min(sample_rate / 2, 8000)
        valid_idx = frequencies <= max_f
        sub_f = frequencies[valid_idx]
        sub_s = spectrum[valid_idx]
        max_amp = np.max(sub_s) if len(sub_s) > 0 and np.max(sub_s) > 0 else 1.0

        plot_w = (w - 20) - 50
        plot_h = (h - 35) - 30
        pts = []
        for f, s in zip(sub_f, sub_s):
            px = int(50 + (f / max_f) * plot_w)
            py = int((h - 35) - (s / max_amp) * plot_h * 0.9)
            pts.append((px, py))

        if len(pts) > 1:
            poly = [(50, h - 35)] + pts + [(pts[-1][0], h - 35)]
            draw.polygon(poly, fill=(195, 228, 248))
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i+1]], fill=(0, 140, 180), width=2)

        # Outer border & Labels
        draw.rectangle([(50, 30), (w - 20, h - 35)], outline=(121, 170, 240), width=1)
        draw.text((w // 2 - 90, 10), "Frequency Contour & Spectrum", fill=(22, 76, 153))
        draw.text((w // 2 - 35, h - 22), "Frequency (Hz)", fill=(22, 76, 153))
        draw.text((8, h // 2 - 10), "Amp", fill=(22, 76, 153))

        st.image(img)
        return img
st.title("Cetacean Interface")
st.caption("HUMAN • CETACEAN COMMUNICATION")

st.markdown("### LIVE OBSERVATION")

image_file = st.file_uploader(
    "Upload an image of the cetacean",
    type=["jpg", "jpeg", "png"]
)

if image_file:
    image = Image.open(image_file)
    st.image(image, caption="Observed scene")

st.markdown("### ACOUSTIC SIGNAL")

audio_file = st.file_uploader(
    "Upload a cetacean recording",
    type=["wav", "mp3", "m4a"]
)

if audio_file:
    st.audio(audio_file)
    st.success("Audio received.")

    evidence = analyze_audio(audio_file)

    st.markdown("### SIGNAL DATA")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "DURATION",
            f'{evidence["duration_seconds"]} s'
        )

    with col2:
        st.metric(
            "PEAK FREQUENCY",
            f'{evidence["dominant_frequency_hz"]} Hz'
        )

    with col3:
        st.metric(
            "AMPLITUDE",
            f'{evidence["average_amplitude"]}'
        )

    generate_signal_graph(evidence["samples"], evidence["sample_rate"])

    images = [image_file.getvalue()] if image_file else []

    st.markdown("### INTERPRETATION")

    if st.button("ANALYSE SIGNAL"):

        with st.spinner("DECODING CETACEAN TRANSMISSION..."):

            try:
                duration_val = evidence["duration_seconds"]
                word_limit = get_speech_length_guideline(duration_val)

                response = ollama.chat(
                    model="gemma3:4b",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
You are part of a SPECULATIVE cetacean communication interface.

Analyse the acoustic measurements below and generate a fictional,
creative interpretation for a design prototype.

ACOUSTIC DATA:
Duration: {duration_val} seconds
Average amplitude: {evidence["average_amplitude"]}
Dominant frequency: {evidence["dominant_frequency_hz"]} Hz

CRITICAL DURATION CONSTRAINT:
The uploaded audio is only {duration_val} seconds long.
The spoken TRANSLATED TRANSMISSION MUST MATCH this short duration:
Target length: EXACTLY {word_limit}.
Do NOT write more words than this. Keep it extremely brief and punchy.

Style: Cetacean Mobster / Noir. Short, cinematic, playful mobster slang.
Examples: "Easy there, pal.", "Watch yourself, capisce?", "You're in our waters.", "Nice boat you got there.", "Keep it moving, buddy.", "We got eyes everywhere."
Do not invent excessive backstory, names, locations, crime families, or long scenarios.

Create a concise fictional interpretation in this format:

SIGNAL TYPE:
[Give a short signal classification]

ACOUSTIC ANALYSIS:
[Brief technical interpretation of the measurements]

TRANSLATED TRANSMISSION:
"[Generate ONE short fictional mobster-style dialogue of {word_limit}, maximum 1-2 short sentences. Put in quotes.]"
""",
                            "images": images
                        }
                    ]
                )

                st.session_state.interpretation = response["message"]["content"]

                # Generate duration-aware TTS audio
                dialogue = extract_transmission_dialogue(st.session_state.interpretation)
                try:
                    st.session_state.tts_audio = generate_tts_audio(dialogue)
                except Exception as tts_e:
                    st.session_state.tts_audio = None

            except Exception as e:
                st.error(f"MODEL CONNECTION ERROR: {e}")

    if st.session_state.interpretation:

        st.warning("INTERPRETATION CONFIDENCE: LOW")

        st.write(st.session_state.interpretation)

        if st.session_state.get("tts_audio"):
            render_frutiger_audio_player(st.session_state.tts_audio)

st.markdown("### SESSION STATUS")

st.markdown("""
<div class="session-status-block">
    <div class="status-item">LOCAL MODEL: GEMMA 3-4B</div>
    <div class="status-item">CONNECTION: LOCAL</div>
</div>
""", unsafe_allow_html=True)

with st.expander("🔑 ELEVENLABS SETTINGS", expanded=not bool(os.environ.get("ELEVENLABS_API_KEY"))):
    if os.environ.get("ELEVENLABS_API_KEY"):
        st.success("🟢 ElevenLabs API Key is active")
    else:
        st.info("⚪ ElevenLabs Key not detected (Currently using local offline voice synthesis)")

    input_key = st.text_input("Paste ElevenLabs API Key:", type="password", key="el_key_input", help="Saved locally to .env and never displayed")
    if st.button("SAVE KEY TO .ENV"):
        clean_key = input_key.strip()
        if clean_key:
            env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
            try:
                with open(env_file_path, "w", encoding="utf-8") as f:
                    f.write(f"ELEVENLABS_API_KEY={clean_key}\nELEVENLABS_VOICE_ID={voice_id}\n")
                os.environ["ELEVENLABS_API_KEY"] = clean_key
                st.success("✅ Saved to .env! ElevenLabs neural TTS is ready.")
                try:
                    st.rerun()
                except Exception:
                    pass
            except Exception:
                st.error("Failed to write to .env file.")