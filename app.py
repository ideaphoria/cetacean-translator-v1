import streamlit as st
import ollama
from PIL import Image, ImageDraw
import subprocess
import tempfile
import os
import numpy as np
import base64
import hashlib
import io
import shutil
import html
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


/* ---------- MAIN COCKPIT DEVICE BODY ---------- */

.block-container {
    width: 96% !important;
    max-width: 1200px !important;
    padding: 24px 28px 20px 28px !important;
    margin: 2.5vh auto !important;

    background:
        radial-gradient(
            ellipse at 25% 6%,
            rgba(255,255,255,1),
            rgba(255,255,255,0) 35%
        ),
        radial-gradient(
            ellipse at 80% 90%,
            rgba(190,225,255,0.7),
            rgba(190,225,255,0) 45%
        ),
        linear-gradient(
            145deg,
            #ffffff 0%,
            #edf5ff 45%,
            #cde1f8 100%
        ) !important;

    border: 2.5px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 42px !important;

    box-shadow:
        0 25px 60px rgba(35, 75, 150, 0.3),
        inset 0 4px 10px rgba(255, 255, 255, 1),
        inset 0 -10px 22px rgba(70, 120, 200, 0.16) !important;

    overflow-x: hidden !important;
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

/* ---------- SIGNAL SOURCE SELECTOR ---------- */
div[data-testid="stRadio"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    margin: 0 auto 1.2rem auto !important;
    width: 100% !important;
}

div[data-testid="stRadio"] > label,
div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
    display: none !important;
}

div[data-testid="stRadio"] > div {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    flex-wrap: wrap !important;
    gap: 12px !important;
    background: rgba(230, 242, 255, 0.75) !important;
    padding: 6px 16px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.9), 0 4px 10px rgba(50, 90, 160, 0.1) !important;
}

div[data-testid="stRadio"] label {
    font-weight: 800 !important;
    color: #164c99 !important;
    cursor: pointer !important;
}

/* ---------- LIVE AUDIO INPUT BLOB ---------- */
[data-testid="stAudioInput"] {
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
    border-radius: 50px 35px 55px 40px !important;
    padding: 16px 20px !important;
    box-shadow:
        0 12px 25px rgba(50,90,160,0.22),
        inset 0 4px 8px rgba(255,255,255,1),
        inset 0 -7px 14px rgba(60,110,190,0.15) !important;
    margin: 1rem auto !important;
    text-align: center !important;
    width: 100% !important;
}

[data-testid="stAudioInput"] label,
[data-testid="stAudioInput"] label p {
    color: #164c99 !important;
    font-weight: 850 !important;
    text-align: center !important;
    letter-spacing: 0.5px !important;
    justify-content: center !important;
}

/* ---------- LIVE STATUS PILL ---------- */
.live-status-pill {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px 18px;
    border-radius: 999px;
    margin: 12px auto 18px auto;
    max-width: 480px;
    background: linear-gradient(150deg, rgba(255,255,255,0.95), rgba(220,238,255,0.85));
    border: 1.5px solid rgba(255,255,255,0.95);
    box-shadow: 0 8px 18px rgba(35,80,160,0.14), inset 0 2px 5px rgba(255,255,255,0.95);
    text-align: center;
}

.live-status-pill .badge-main {
    color: #164c99;
    font-size: 0.92rem;
    letter-spacing: 0.6px;
}

.live-status-pill .badge-sub {
    color: #3b6ba8;
    font-size: 0.76rem;
    font-weight: 700;
    margin-top: 2px;
    letter-spacing: 0.4px;
}

.live-status-pill.status-listening {
    border-color: rgba(255, 100, 100, 0.85);
    box-shadow: 0 0 16px rgba(255, 70, 70, 0.35), inset 0 2px 5px rgba(255,255,255,0.95);
}

.live-status-pill.status-ready {
    border-color: rgba(0, 180, 255, 0.85);
    box-shadow: 0 0 16px rgba(0, 180, 255, 0.3), inset 0 2px 5px rgba(255,255,255,0.95);
}

.live-status-pill.status-rejected {
    border-color: rgba(255, 160, 60, 0.85);
    box-shadow: 0 0 16px rgba(255, 130, 40, 0.25), inset 0 2px 5px rgba(255,255,255,0.95);
}

.live-status-pill.status-complete {
    border-color: rgba(60, 210, 150, 0.85);
    box-shadow: 0 0 16px rgba(40, 190, 120, 0.25), inset 0 2px 5px rgba(255,255,255,0.95);
}

/* ---------- SIGNAL REJECTED CARD ---------- */
.signal-rejected-card {
    background:
        radial-gradient(ellipse at 30% 15%, rgba(255,255,255,0.98), rgba(255,240,240,0.6) 45%),
        linear-gradient(155deg, rgba(255,245,245,0.95) 0%, rgba(255,225,225,0.85) 50%, rgba(255,200,200,0.9) 100%);
    border-radius: 40px 55px 38px 48px;
    border: 2px solid rgba(255, 255, 255, 0.95);
    box-shadow:
        0 16px 32px rgba(180, 60, 60, 0.2),
        inset 0 3px 6px rgba(255,255,255,0.95),
        inset 0 -6px 14px rgba(180, 40, 40, 0.15);
    padding: 22px 26px;
    margin: 20px auto;
    text-align: center;
    max-width: 540px;
}

.signal-rejected-card .rejected-title {
    color: #b52b2b;
    font-size: 1.25rem;
    font-weight: 900;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}

.signal-rejected-card .rejected-sub {
    color: #8c2525;
    font-size: 0.92rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.signal-rejected-card .rejected-status {
    color: #a85858;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

/* ---------- SYSTEM STATUS ROTATING CYCLER ---------- */
.status-cycler-container {
    height: 24px;
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 4px auto;
}

.status-cycler-msg {
    position: absolute;
    width: 100%;
    text-align: center;
    color: #164c99;
    font-weight: 850;
    font-size: 0.92rem;
    letter-spacing: 0.5px;
    opacity: 0;
    animation: statusCycleAnim 6s infinite ease-in-out;
}

.status-cycler-msg.msg-1 { animation-delay: 0s; }
.status-cycler-msg.msg-2 { animation-delay: 1.5s; }
.status-cycler-msg.msg-3 { animation-delay: 3.0s; }
.status-cycler-msg.msg-4 { animation-delay: 4.5s; }

@keyframes statusCycleAnim {
    0% {
        opacity: 0;
        transform: translateY(10px);
    }
    4% {
        opacity: 1;
        transform: translateY(0);
    }
    23% {
        opacity: 1;
        transform: translateY(0);
    }
    27% {
        opacity: 0;
        transform: translateY(-10px);
    }
    100% {
        opacity: 0;
        transform: translateY(-10px);
    }
}

.analysing-status-pod {
    background:
        radial-gradient(ellipse at 30% 15%, rgba(255,255,255,0.98), rgba(220,240,255,0.7) 45%),
        linear-gradient(155deg, rgba(245,252,255,0.95) 0%, rgba(200,230,255,0.85) 50%, rgba(150,200,250,0.9) 100%);
    border-radius: 999px;
    border: 1.5px solid rgba(255,255,255,0.95);
    box-shadow:
        0 8px 20px rgba(35,80,160,0.18),
        inset 0 2px 5px rgba(255,255,255,1);
    padding: 8px 20px;
    margin: 12px auto;
    max-width: 480px;
    text-align: center;
}

/* =========================================================
   COCKPIT TELEMETRY HEADER & TELEMETRY ROW
   ========================================================= */

.cockpit-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background:
        radial-gradient(ellipse at 30% 12%, rgba(255,255,255,0.98), rgba(225,242,255,0.7) 40%),
        linear-gradient(155deg, rgba(250,253,255,0.95) 0%, rgba(205,232,255,0.85) 50%, rgba(160,208,252,0.9) 100%);
    border: 2px solid rgba(255, 255, 255, 0.95);
    border-radius: 999px;
    padding: 8px 18px;
    margin-bottom: 8px;
    box-shadow:
        0 8px 20px rgba(35, 80, 160, 0.16),
        inset 0 2px 5px rgba(255,255,255,0.95),
        inset 0 -3px 8px rgba(40,100,190,0.12);
    flex-wrap: wrap;
    gap: 8px;
}

.cockpit-logo-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.cockpit-icon {
    font-size: 1.4rem;
    filter: drop-shadow(0 2px 4px rgba(0, 100, 200, 0.3));
}

.cockpit-title {
    font-size: 1.05rem;
    font-weight: 900;
    letter-spacing: 0.8px;
    color: #104080;
    text-shadow: 0 1px 0 rgba(255,255,255,0.9);
    line-height: 1.1;
}

.cockpit-subtitle {
    font-size: 0.65rem;
    font-weight: 750;
    letter-spacing: 0.8px;
    color: #386ba8;
}

.cockpit-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 999px;
    padding: 4px 12px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.06), 0 2px 6px rgba(0,120,255,0.1);
    font-size: 0.72rem;
    font-weight: 800;
    color: #0b5535;
    letter-spacing: 0.5px;
}

.led-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.green-pulsing {
    background: #00e676;
    box-shadow: 0 0 8px #00e676;
    animation: ledPulse 2s infinite ease-in-out;
}

@keyframes ledPulse {
    0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 8px #00e676; }
    50% { opacity: 0.6; transform: scale(0.9); box-shadow: 0 0 3px #00e676; }
}

.signal-bars {
    display: inline-flex;
    align-items: flex-end;
    gap: 2px;
    height: 10px;
}
.signal-bars span {
    display: inline-block;
    width: 2.5px;
    background: #00b0ff;
    border-radius: 1px;
}
.signal-bars span:nth-child(1) { height: 3px; }
.signal-bars span:nth-child(2) { height: 5px; }
.signal-bars span:nth-child(3) { height: 8px; }
.signal-bars span:nth-child(4) { height: 10px; }

.header-right {
    display: flex;
    align-items: center;
    gap: 8px;
}

.telemetry-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(220, 240, 255, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: #124e88;
    font-weight: 700;
}

.battery-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(220, 240, 255, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: #124e88;
    font-weight: 800;
}

.battery-bar {
    width: 24px;
    height: 9px;
    border: 1px solid #124e88;
    border-radius: 2px;
    padding: 1px;
    display: inline-block;
}
.battery-fill {
    width: 86%;
    height: 100%;
    background: #00e676;
    border-radius: 1px;
}

.environmental-telemetry-row,
.system-telemetry-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}

.env-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.68rem;
    color: #104080;
    font-weight: 750;
    box-shadow: 0 2px 6px rgba(35, 75, 140, 0.08);
}

.env-chip .chip-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00d2ff;
    box-shadow: 0 0 5px #00d2ff;
}

/* =========================================================
   PANEL SECTION HEADERS (Observation & Signal)
   ========================================================= */

.panel-section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    background:
        radial-gradient(ellipse at 30% 15%, rgba(255,255,255,0.95), rgba(220,240,255,0.7) 45%),
        linear-gradient(155deg, rgba(245,252,255,0.95) 0%, rgba(200,230,255,0.85) 50%, rgba(160,210,252,0.9) 100%);
    border: 1.5px solid rgba(255, 255, 255, 0.95);
    border-radius: 999px;
    padding: 6px 14px;
    margin: 4px 0 10px 0;
    box-shadow: 0 4px 12px rgba(35, 80, 150, 0.12), inset 0 2px 4px rgba(255,255,255,0.95);
}

.panel-led {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00e676;
    box-shadow: 0 0 8px #00e676;
}

.panel-title {
    color: #104080;
    font-size: 0.82rem;
    font-weight: 850;
    letter-spacing: 0.8px;
    text-shadow: 0 1px 0 rgba(255,255,255,0.9);
}

.panel-tag {
    margin-left: auto;
    background: rgba(10, 45, 90, 0.75);
    color: #ffffff;
    font-size: 0.62rem;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 999px;
    letter-spacing: 0.6px;
}

/* =========================================================
   STANDBY ACOUSTIC RADAR CARD
   ========================================================= */

.standby-spectrogram-pod {
    background:
        radial-gradient(ellipse at 30% 8%, rgba(255,255,255,0.98), rgba(255,255,255,0.45) 40%, rgba(205,235,255,0.7) 75%),
        linear-gradient(155deg, rgba(245,252,255,0.95) 0%, rgba(195,228,255,0.85) 50%, rgba(145,198,245,0.9) 100%);
    border: 2px solid rgba(255, 255, 255, 0.95);
    border-radius: 28px;
    padding: 12px 14px;
    box-shadow:
        0 12px 28px rgba(35, 80, 150, 0.18),
        inset 0 3px 6px rgba(255, 255, 255, 0.95),
        inset 0 -5px 12px rgba(40, 100, 190, 0.15);
    margin-bottom: 12px;
}

.spec-header-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.spec-led-green {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00e676;
    box-shadow: 0 0 6px #00e676;
}

.spec-title {
    color: #104080;
    font-size: 0.8rem;
    font-weight: 850;
    letter-spacing: 0.8px;
}

.spec-tabs {
    margin-left: auto;
    display: flex;
    gap: 4px;
}

.spec-tab {
    font-size: 0.62rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 999px;
    background: rgba(220, 235, 255, 0.8);
    color: #124e88;
}
.spec-tab.active {
    background: #0077e6;
    color: #ffffff;
    box-shadow: 0 2px 6px rgba(0,100,220,0.3);
}

.spec-screen-viewport {
    width: 100%;
    height: 140px;
    background: #06162a;
    border: 2px solid rgba(255, 255, 255, 0.85);
    border-radius: 18px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: inset 0 4px 12px rgba(0,0,0,0.6), 0 2px 6px rgba(30,70,140,0.15);
}

.radar-grid {
    position: absolute;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 229, 255, 0.25);
    box-shadow: 0 0 0 25px rgba(0, 229, 255, 0.05), inset 0 0 15px rgba(0, 229, 255, 0.08);
    pointer-events: none;
}

.radar-scanline {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg, rgba(0,229,255,0) 0%, rgba(0,229,255,0.12) 50%, rgba(0,229,255,0) 100%);
    animation: radarScan 3s linear infinite;
    pointer-events: none;
}

@keyframes radarScan {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}

.standby-spec-text-row {
    color: #00e5ff;
    font-size: 0.75rem;
    font-weight: 850;
    letter-spacing: 0.8px;
    display: flex;
    align-items: center;
    gap: 6px;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.6);
}

.standby-spec-sub {
    color: #6fa0d8;
    font-size: 0.62rem;
    font-weight: 650;
    margin-top: 4px;
}

.spec-metrics-placeholder {
    display: flex;
    gap: 6px;
    margin-top: 8px;
}

.metric-chip {
    flex: 1;
    text-align: center;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    padding: 3px 6px;
    font-size: 0.65rem;
    color: #104080;
    font-weight: 700;
}

/* =========================================================
   INTERPRETATION BUBBLE POD
   ========================================================= */

.interpretation-bubble-pod {
    background:
        radial-gradient(ellipse at 30% 10%, rgba(255,255,255,0.98), rgba(230,245,255,0.7) 40%),
        linear-gradient(155deg, rgba(250,253,255,0.96) 0%, rgba(210,235,255,0.88) 50%, rgba(165,212,255,0.92) 100%);
    border: 2px solid rgba(255, 255, 255, 0.95);
    border-radius: 24px;
    padding: 10px 14px;
    box-shadow:
        0 10px 24px rgba(35, 80, 160, 0.16),
        inset 0 3px 6px rgba(255,255,255,0.95),
        inset 0 -5px 12px rgba(40,100,190,0.14);
    margin: 8px 0;
}

.interp-header-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}

.dolphin-emblem {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 25%, #ffffff 0%, #4facfe 50%, #0066cc 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 10px rgba(0,180,255,0.4), inset 0 1px 3px rgba(255,255,255,0.9);
    font-size: 1.05rem;
}

.interp-title-col {
    display: flex;
    flex-direction: column;
}

.interp-tag {
    color: #104080;
    font-size: 0.72rem;
    font-weight: 850;
    letter-spacing: 0.6px;
}

.interp-sub {
    color: #386ba8;
    font-size: 0.58rem;
    font-weight: 700;
}

.confidence-badge {
    margin-left: auto;
    background: rgba(255, 200, 60, 0.25);
    border: 1px solid rgba(230, 160, 20, 0.6);
    color: #925800;
    border-radius: 999px;
    padding: 2px 7px;
    font-size: 0.62rem;
    font-weight: 800;
}

.interp-quote-box {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 14px;
    padding: 8px 12px;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.04);
}

.quote-text {
    color: #0c3366;
    font-size: 0.85rem;
    font-weight: 750;
    line-height: 1.35;
}

/* =========================================================
   FLOATING BOTTOM NAVIGATION DOCK
   ========================================================= */

.floating-dock-container {
    display: flex;
    justify-content: center;
    margin: 12px auto 4px auto;
    width: 100%;
}

.floating-dock {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background:
        radial-gradient(ellipse at 30% 15%, rgba(255,255,255,0.98), rgba(230,245,255,0.7) 45%),
        linear-gradient(155deg, rgba(250,253,255,0.95) 0%, rgba(205,232,255,0.85) 50%, rgba(160,208,252,0.9) 100%);
    border: 2px solid rgba(255, 255, 255, 0.95);
    border-radius: 999px;
    padding: 4px 10px;
    box-shadow:
        0 8px 22px rgba(35, 80, 160, 0.2),
        inset 0 2px 5px rgba(255,255,255,0.95);
}

.dock-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 800;
    color: #124e88;
}

.dock-item.active {
    background: #0078ea;
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 110, 230, 0.4), inset 0 1px 2px rgba(255,255,255,0.8);
}

.dock-icon {
    font-size: 0.8rem;
}

/* =========================================================
   RESPONSIVE DESIGN & HARDWARE FORM FACTOR OPTIMIZATIONS
   ========================================================= */

/* Ensure whole page prevents unwanted horizontal scrolling */
html, body {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* Base button touch target guarantee */
button[kind="primary"], div.stButton > button {
    min-height: 44px !important;
    font-family: inherit !important;
}

/* ---------- 1. TABLET / iPAD LANDSCAPE (769px to 1200px width, min-height 501px) ---------- */
@media (min-width: 769px) and (max-width: 1200px) and (min-height: 501px) {
    .block-container {
        width: 96vw !important;
        max-width: 1200px !important;
        margin: 12px auto !important;
        padding: 16px 20px !important;
        border-radius: 32px !important;
        overflow-x: hidden !important;
    }

    .block-container > div > [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 14px !important;
        align-items: stretch !important;
    }

    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: calc(50% - 7px) !important;
        min-width: calc(50% - 7px) !important;
        flex: 1 1 0px !important;
    }

    .cockpit-header-bar {
        padding: 6px 16px;
        margin-bottom: 8px;
    }

    .cockpit-title {
        font-size: clamp(0.85rem, 1.8vw, 1.1rem);
    }

    [data-testid="stMetric"] {
        padding: 8px 10px !important;
        border-radius: 20px !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }

    .spec-screen-viewport {
        height: 160px;
    }
}

/* ---------- 2. TABLET / iPAD PORTRAIT (601px to 900px width, portrait) ---------- */
@media (min-width: 601px) and (max-width: 900px) and (orientation: portrait) {
    .block-container {
        width: 95vw !important;
        max-width: 95vw !important;
        margin: 10px auto !important;
        padding: 16px 18px !important;
        border-radius: 30px !important;
        overflow-x: hidden !important;
    }

    /* Primary cockpit columns stack cleanly in vertical flow */
    .block-container > div > [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 16px !important;
    }

    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Inner rows (such as telemetry metrics row) remain side-by-side */
    [data-testid="stHorizontalBlock"]:not(.block-container > div > [data-testid="stHorizontalBlock"]) {
        display: flex !important;
        flex-direction: row !important;
        gap: 10px !important;
    }

    [data-testid="stHorizontalBlock"]:not(.block-container > div > [data-testid="stHorizontalBlock"]) > [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0px !important;
    }

    [data-testid="stMetric"] {
        padding: 10px 12px !important;
        border-radius: 22px !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.74rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }

    .spec-screen-viewport {
        height: 180px;
    }
}

/* ---------- 3. COMPACT LANDSCAPE PHONE (orientation: landscape and max-height: 500px) ---------- */
@media (orientation: landscape) and (max-height: 500px) {
    .block-container {
        width: 98vw !important;
        max-width: 98vw !important;
        margin: 2px auto !important;
        padding: 5px 10px 8px 10px !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 20px rgba(30, 65, 140, 0.2) !important;
        overflow-x: hidden !important;
    }

    .block-container > div > [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 8px !important;
        align-items: stretch !important;
    }

    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: calc(50% - 4px) !important;
        min-width: calc(50% - 4px) !important;
        flex: 1 1 0px !important;
    }

    .cockpit-header-bar {
        padding: 4px 10px;
        margin-bottom: 4px;
    }

    .cockpit-title {
        font-size: clamp(0.75rem, 1.8vw, 0.88rem);
    }

    .cockpit-subtitle {
        font-size: 0.62rem;
    }

    .environmental-telemetry-row,
    .system-telemetry-row {
        margin-bottom: 4px;
        gap: 3px;
    }

    .env-chip {
        font-size: 0.6rem;
        padding: 1px 5px;
    }

    button[kind="primary"], div.stButton > button {
        min-height: 44px !important;
        font-size: 0.84rem !important;
        padding: 6px 12px !important;
    }

    div[data-testid="stRadio"] label {
        font-size: 0.7rem !important;
        padding: 2px 6px !important;
    }

    /* Compact telemetry metrics */
    [data-testid="stHorizontalBlock"]:not(.block-container > div > [data-testid="stHorizontalBlock"]) {
        display: flex !important;
        flex-direction: row !important;
        gap: 4px !important;
    }

    [data-testid="stHorizontalBlock"]:not(.block-container > div > [data-testid="stHorizontalBlock"]) > [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0px !important;
    }

    [data-testid="stMetric"] {
        padding: 4px 5px !important;
        border-radius: 14px !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.58rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 0.88rem !important;
    }

    .spec-screen-viewport {
        height: 110px;
    }

    .quote-text {
        font-size: 0.76rem;
    }
}

/* ---------- 4. PORTRAIT MOBILE PHONES (max-width: 600px) ---------- */
@media (max-width: 600px) {
    .block-container {
        width: 96vw !important;
        max-width: 96vw !important;
        margin: 4px auto !important;
        padding: 10px 10px 16px 10px !important;
        border-radius: 24px !important;
        overflow-x: hidden !important;
    }

    /* Primary cockpit columns stack cleanly in vertical flow */
    .block-container > div > [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 14px !important;
    }

    .block-container > div > [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    .cockpit-header-bar {
        padding: 6px 10px;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: center;
    }

    .header-right {
        gap: 4px;
        flex-wrap: wrap;
        justify-content: center;
    }

    .cockpit-title {
        font-size: 0.9rem;
    }

    .cockpit-subtitle {
        font-size: 0.65rem;
    }

    .environmental-telemetry-row,
    .system-telemetry-row {
        flex-wrap: wrap;
        justify-content: center;
        gap: 4px;
    }

    .env-chip {
        font-size: 0.64rem;
        padding: 2px 6px;
    }

    /* Radio button bar wraps cleanly with tap-friendly pill buttons */
    div[data-testid="stRadio"] > div {
        flex-direction: column !important;
        border-radius: 24px !important;
        padding: 8px 14px !important;
        width: 100% !important;
        gap: 6px !important;
        align-items: flex-start !important;
    }

    div[data-testid="stRadio"] label {
        font-size: 0.74rem !important;
        padding: 6px 10px !important;
        min-height: 40px !important;
        width: 100% !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    /* Telemetry metrics remain in a 3-pill row */
    [data-testid="stHorizontalBlock"]:not(.block-container > div > [data-testid="stHorizontalBlock"]) {
        display: flex !important;
        flex-direction: row !important;
        gap: 6px !important;
    }

    [data-testid="stHorizontalBlock"]:not(.block-container > div > [data-testid="stHorizontalBlock"]) > [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0px !important;
    }

    [data-testid="stMetric"] {
        padding: 6px 6px !important;
        border-radius: 18px !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.62rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 0.92rem !important;
    }

    button[kind="primary"], div.stButton > button {
        min-height: 44px !important;
        width: 100% !important;
        font-size: 0.88rem !important;
        padding: 8px 16px !important;
    }

    .spec-screen-viewport {
        height: 140px;
    }

    .quote-text {
        font-size: 0.8rem;
    }
}
</style>
""".replace("__BG_IMAGE__", bg_image), unsafe_allow_html=True)
if "interpretation" not in st.session_state:
    st.session_state.interpretation = None
if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None
if "live_state" not in st.session_state:
    st.session_state.live_state = "Idle"
if "live_recorded_audio" not in st.session_state:
    st.session_state.live_recorded_audio = None
if "live_audio_hash" not in st.session_state:
    st.session_state.live_audio_hash = None
if "live_rejected" not in st.session_state:
    st.session_state.live_rejected = False
if "upload_rejected" not in st.session_state:
    st.session_state.upload_rejected = False
if "multimodal_state" not in st.session_state:
    st.session_state.multimodal_state = "Idle"
if "captured_video" not in st.session_state:
    st.session_state.captured_video = None
if "captured_audio" not in st.session_state:
    st.session_state.captured_audio = None
if "last_multimodal_hash" not in st.session_state:
    st.session_state.last_multimodal_hash = None
if "multimodal_rejected" not in st.session_state:
    st.session_state.multimodal_rejected = False
if "multimodal_error" not in st.session_state:
    st.session_state.multimodal_error = None
if "ollama_warmed" not in st.session_state:
    st.session_state.ollama_warmed = True
    def _warmup_ollama():
        try:
            import ollama
            ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": "ping"}], keep_alive="1h")
        except Exception:
            pass
    import threading
    threading.Thread(target=_warmup_ollama, daemon=True).start()

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
    """Randomly choose one Voice ID strictly from ELEVENLABS_VOICE_IDS."""
    valid_voices = [v.strip() for v in ELEVENLABS_VOICE_IDS if isinstance(v, str) and v.strip()]
    if valid_voices:
        return random.choice(valid_voices)
    return None

def generate_tts_audio(text):
    if not text or not text.strip():
        return None
    clean_text = text.strip('"\'\n\r ')

    # ElevenLabs TTS (strictly using approved ELEVENLABS_VOICE_IDS)
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    valid_voices = [v.strip() for v in ELEVENLABS_VOICE_IDS if isinstance(v, str) and v.strip()]
    if not valid_voices or not api_key:
        return None

    # Randomly shuffle approved voices to try a random approved voice each time,
    # with seamless fallback to another approved voice if the account tier restricts a specific voice.
    candidate_voices = list(valid_voices)
    random.shuffle(candidate_voices)

    for voice_id in candidate_voices:
        try:
            import requests
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
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200 and resp.content:
                return resp.content
        except Exception:
            continue

    # Never generate a robot or default voice (macOS say, gTTS, pyttsx3 removed).
    # If ElevenLabs is not configured or no approved voice succeeds, fail gracefully with no audio.
    return None

generate_translation_audio = generate_tts_audio

def extract_transmission_dialogue(full_text):
    if not full_text:
        return ""
    import re

    # 1. Search line-by-line for TRANSLATED TRANSMISSION header
    lines = full_text.split("\n")
    found_header = False
    for line in lines:
        clean_l = line.strip().strip("*_# ")
        if "TRANSLATED TRANSMISSION" in clean_l.upper():
            found_header = True
            if ":" in line:
                after_colon = line.split(":", 1)[1].strip().strip("*_\"' ")
                if after_colon and not after_colon.startswith("["):
                    return after_colon
            continue
        if found_header:
            candidate = clean_l.strip('"\'')
            if candidate and not candidate.startswith("[") and not candidate.startswith("#"):
                return candidate

    # 2. Search for any dialogue in quotes
    quotes = re.findall(r'["\']([^"\'\n]{2,120})["\']', full_text)
    if quotes:
        for q in reversed(quotes):
            cq = q.strip().strip("*_\"' ")
            if cq and not cq.startswith("["):
                return cq

    # 3. Fallback to last non-empty line
    non_empty = [l.strip().strip("*_\"' ") for l in lines if l.strip().strip("*_\"' ")]
    if non_empty:
        return non_empty[-1]
    return ""
def render_analysing_status():
    return """
    <div class="analysing-status-pod">
        <div style="font-size: 0.76rem; font-weight: 800; color: #20559a; letter-spacing: 0.8px; margin-bottom: 2px;">SYSTEM STATUS: ANALYSING</div>
        <div class="status-cycler-container">
            <div class="status-cycler-msg msg-1">Scanning acoustic signal…</div>
            <div class="status-cycler-msg msg-2">Mapping frequency contours…</div>
            <div class="status-cycler-msg msg-3">Checking cetacean plausibility…</div>
            <div class="status-cycler-msg msg-4">Decoding transmission…</div>
        </div>
    </div>
    """

def render_frutiger_recording_player(audio_file):
    if audio_file is None:
        return
    try:
        if isinstance(audio_file, (bytes, bytearray)):
            audio_bytes = bytes(audio_file)
        elif hasattr(audio_file, "getvalue"):
            audio_bytes = audio_file.getvalue()
        elif hasattr(audio_file, "read"):
            pos = audio_file.tell() if hasattr(audio_file, "tell") else 0
            audio_file.seek(0)
            audio_bytes = audio_file.read()
            audio_file.seek(pos)
        else:
            return
    except Exception:
        return

    if not audio_bytes:
        return

    b64_audio = base64.b64encode(audio_bytes).decode()
    if audio_bytes.startswith(b"RIFF"):
        mime_type = "audio/wav"
    elif audio_bytes.startswith(b"ID3") or (len(audio_bytes) > 2 and audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        mime_type = "audio/mpeg"
    elif audio_bytes.startswith(b"OggS"):
        mime_type = "audio/ogg"
    elif len(audio_bytes) > 8 and audio_bytes[4:8] == b"ftyp":
        mime_type = "audio/mp4"
    else:
        mime_type = "audio/wav"

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
      padding: 4px 0;
      overflow: hidden;
    }}
    .frutiger-rec-pod {{
      width: 100%;
      max-width: 580px;
      background:
        radial-gradient(ellipse at 30% 12%, rgba(255,255,255,0.98), rgba(255,255,255,0.55) 35%, rgba(215,238,255,0.8) 75%),
        linear-gradient(155deg, rgba(245,252,255,0.96) 0%, rgba(195,228,255,0.9) 50%, rgba(150,200,248,0.92) 100%);
      border-radius: 999px;
      border: 2px solid rgba(255,255,255,0.95);
      box-shadow:
        0 10px 24px rgba(35,80,150,0.18),
        inset 0 2.5px 6px rgba(255,255,255,0.95),
        inset 0 -3px 8px rgba(40,100,190,0.16);
      padding: 8px 16px;
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .frutiger-rec-pod::before {{
      content: "";
      position: absolute;
      top: 0; left: 12%; right: 12%;
      height: 12px;
      background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0) 100%);
      border-radius: 0 0 50% 50%;
      pointer-events: none;
    }}
    .play-btn {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      border: 2px solid rgba(255,255,255,0.95);
      background: radial-gradient(circle at 35% 25%, #ffffff 0%, #6ec2ff 45%, #186edb 80%, #0c438c 100%);
      box-shadow:
        0 4px 10px rgba(20,70,150,0.3),
        inset 0 2px 4px rgba(255,255,255,0.9),
        inset 0 -2px 5px rgba(0,30,80,0.35);
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-shrink: 0;
      outline: none;
      transition: transform 0.1s, box-shadow 0.1s;
    }}
    .play-btn:hover {{
      transform: scale(1.06);
      box-shadow: 0 6px 14px rgba(20,70,150,0.4), inset 0 2px 5px rgba(255,255,255,1);
    }}
    .play-btn:active {{
      transform: scale(0.95);
      box-shadow: inset 0 3px 6px rgba(0,30,80,0.45);
    }}
    .play-icon {{
      width: 14px;
      height: 14px;
      fill: #ffffff;
      filter: drop-shadow(0 1px 1px rgba(0,20,60,0.4));
    }}
    .rec-info-col {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
    }}
    .rec-meta-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 2px;
    }}
    .rec-title {{
      color: #104080;
      font-size: 11px;
      font-weight: 850;
      letter-spacing: 0.6px;
      text-shadow: 0 1px 0 rgba(255,255,255,0.9);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .rec-time {{
      color: #20589a;
      font-size: 10px;
      font-weight: 750;
      letter-spacing: 0.5px;
      flex-shrink: 0;
    }}
    .progress-track {{
      height: 8px;
      background: rgba(185,215,245,0.65);
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.9);
      box-shadow: inset 0 1.5px 3px rgba(20,60,130,0.22);
      position: relative;
      cursor: pointer;
      overflow: hidden;
    }}
    .progress-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #00d4ff 0%, #0088ff 70%, #00f0ff 100%);
      border-radius: 999px;
      box-shadow: 0 0 8px rgba(0,212,255,0.7);
      transition: width 0.08s linear;
    }}
    .volume-group {{
      display: flex;
      align-items: center;
      gap: 5px;
      flex-shrink: 0;
    }}
    .vol-icon {{
      width: 13px;
      height: 13px;
      fill: #185ba5;
    }}
    .vol-slider {{
      -webkit-appearance: none;
      width: 52px;
      height: 5px;
      border-radius: 999px;
      background: rgba(185,215,245,0.7);
      outline: none;
      border: 1px solid rgba(255,255,255,0.8);
      box-shadow: inset 0 1px 2px rgba(20,60,130,0.2);
    }}
    .vol-slider::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 25%, #ffffff 0%, #6ec2ff 50%, #186edb 100%);
      border: 1px solid rgba(255,255,255,0.95);
      cursor: pointer;
      box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }}
    </style>
    </head>
    <body>
    <div class="frutiger-rec-pod">
      <button class="play-btn" id="playBtn" title="Play / Pause Recording">
        <svg class="play-icon" id="playIcon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
      </button>
      <div class="rec-info-col">
        <div class="rec-meta-row">
          <span class="rec-title">CETACEAN AUDIO RECORDING</span>
          <span class="rec-time"><span id="currTime">0:00</span> / <span id="durTime">0:00</span></span>
        </div>
        <div class="progress-track" id="progressTrack">
          <div class="progress-fill" id="progressFill"></div>
        </div>
      </div>
      <div class="volume-group">
        <svg class="vol-icon" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
        <input type="range" class="vol-slider" id="volSlider" min="0" max="1" step="0.05" value="1">
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
        if (audio.paused) {{
          audio.play();
        }} else {{
          audio.pause();
        }}
      }});

      audio.addEventListener("play", () => {{
        playIcon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
      }});

      audio.addEventListener("pause", () => {{
        playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
      }});

      audio.addEventListener("ended", () => {{
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
    }})();
    </script>
    </body>
    </html>
    """
    st.components.v1.html(player_html, height=72)

# =========================================================
# MULTIMODAL CAPTURE COMPONENT & HELPERS
# =========================================================
_multimodal_comp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multimodal_recorder")
multimodal_capture_component = st.components.v1.declare_component("multimodal_recorder", path=_multimodal_comp_dir)

def _log_multimodal_diagnostics(python_type, first_50, payload_len, detected_mime, decoded_len):
    """Log media handoff diagnostics safely without crashing if stdout/stderr is unavailable."""
    try:
        print("=" * 60)
        print("[MULTIMODAL DIAGNOSTICS - TERMINAL ONLY]")
        print(f"  • Python type of the received payload : {python_type}")
        print(f"  • First 50 characters of the payload  : {repr(first_50)}")
        print(f"  • Payload length                      : {payload_len}")
        print(f"  • Detected MIME type                  : {detected_mime}")
        print(f"  • Decoded byte length                 : {decoded_len}")
        print("=" * 60)
    except Exception:
        pass

def verify_video_playable(video_bytes):
    """
    Validate that video bytes form a valid, non-empty media container in-memory.
    Avoids spawning heavy external decoders that trigger OS memory kills (exit code -9).
    """
    if not video_bytes or len(video_bytes) < 100:
        return False, "Empty or truncated video payload (< 100 bytes)."

    # 1. WebM / Matroska EBML signature (\x1a\x45\xdf\xa3)
    if video_bytes.startswith(b"\x1aE\xdf\xa3"):
        return True, None

    # 2. MP4 / ISO Base Media signatures (ftyp, moov, mdat, etc.)
    if len(video_bytes) > 8 and (video_bytes[4:8] in (b"ftyp", b"moov", b"mdat", b"wide", b"free", b"skip") or video_bytes.startswith(b"\x00\x00\x00")):
        return True, None

    # 3. Ogg or RIFF container signatures
    if video_bytes.startswith(b"OggS") or video_bytes.startswith(b"RIFF"):
        return True, None

    return False, "Unrecognized media format: missing standard WebM or MP4 container header."

def extract_audio_from_video(video_bytes):
    """
    Extract 16kHz mono WAV audio from webm/mp4 video bytes using ffmpeg safely.
    Returns (audio_bytes, error_message).
    """
    if not video_bytes or len(video_bytes) == 0:
        return None, "Empty video payload (0 bytes)."
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        return None, "FFmpeg binary not found on system."

    # Determine file extension based on magic bytes
    ext = ".mp4" if (len(video_bytes) > 8 and video_bytes[4:8] in (b"ftyp", b"moov", b"mdat")) else ".webm"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as vf:
        vf.write(video_bytes)
        v_path = vf.name
    a_path = v_path + ".wav"

    try:
        res = subprocess.run([
            ffmpeg_bin, "-y", "-nostdin",
            "-threads", "1",
            "-analyzeduration", "2000000",
            "-probesize", "2000000",
            "-i", v_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            a_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)

        if res.returncode == 0 and os.path.exists(a_path) and os.path.getsize(a_path) > 0:
            with open(a_path, "rb") as af:
                return af.read(), None

        stderr_text = res.stderr.decode("utf-8", errors="ignore")
        if "does not contain any stream" in stderr_text:
            return None, "No audio stream found in recording. Please ensure microphone access is permitted."
        elif res.returncode in (-9, 137):
            return None, "Audio extraction was interrupted by system memory limits. Please retry with a shorter capture."
        else:
            first_err = [line.strip() for line in stderr_text.splitlines() if "Error" in line or "error" in line]
            err_detail = first_err[-1] if first_err else f"Exit code {res.returncode}"
            return None, f"Audio extraction failed: {err_detail[:100]}"
    except subprocess.TimeoutExpired:
        return None, "Audio extraction timed out after 15 seconds."
    except Exception as e:
        return None, f"Audio extraction error: {e}"
    finally:
        if os.path.exists(v_path):
            try: os.remove(v_path)
            except Exception: pass
        if os.path.exists(a_path):
            try: os.remove(a_path)
            except Exception: pass

def process_captured_media_payload(raw_payload):
    """
    Accept Data URL from browser MediaRecorder, validate, decode Base64,
    verify playability, and extract audio. Logs diagnostics safely.
    """
    python_type = type(raw_payload).__name__
    payload_str = str(raw_payload) if raw_payload is not None else ""
    first_50 = payload_str[:50]
    payload_len = len(payload_str)
    detected_mime = "unknown"
    decoded_bytes = None

    # Step 1: Validate payload string
    if not raw_payload or not isinstance(raw_payload, str):
        _log_multimodal_diagnostics(python_type, first_50, payload_len, detected_mime, 0)
        return None, None, "Invalid or empty media payload received from browser."

    clean_payload = raw_payload.strip()

    # Step 2: Validate that it begins with data:video/ (or expected media MIME type)
    if not clean_payload.startswith("data:video/"):
        _log_multimodal_diagnostics(python_type, first_50, payload_len, detected_mime, 0)
        return None, None, f"Unsupported media format. Expected data:video/... but got: {clean_payload[:25]}"

    # Step 3: Split only at the first comma
    if "," not in clean_payload:
        _log_multimodal_diagnostics(python_type, first_50, payload_len, detected_mime, 0)
        return None, None, "Malformed Data URL: missing separator comma."

    header, b64_payload = clean_payload.split(",", 1)

    # Extract detected MIME type from header (e.g. data:video/webm;base64 -> video/webm)
    if ";" in header:
        detected_mime = header.split(";", 1)[0].replace("data:", "").strip()
    else:
        detected_mime = header.replace("data:", "").strip()

    # Step 4: Decode the payload using Base64
    b64_clean = "".join(b64_payload.split())
    b64_clean += "=" * (-len(b64_clean) % 4)
    try:
        decoded_bytes = base64.b64decode(b64_clean)
    except Exception as e:
        _log_multimodal_diagnostics(python_type, first_50, payload_len, detected_mime, 0)
        return None, None, f"Base64 decoding failed: {e}"

    decoded_len = len(decoded_bytes) if decoded_bytes else 0
    _log_multimodal_diagnostics(python_type, first_50, payload_len, detected_mime, decoded_len)

    # Step 5: Verify resulting file is non-empty and has valid container structure
    if not decoded_bytes or len(decoded_bytes) == 0:
        return None, None, "Decoded video file is empty (0 bytes)."

    is_playable, play_err = verify_video_playable(decoded_bytes)
    if not is_playable:
        return None, None, f"Captured video is not playable: {play_err}"

    # Step 6: Extract audio from the verified video using FFmpeg (audio only, -vn)
    extracted_audio, audio_err = extract_audio_from_video(decoded_bytes)
    if not extracted_audio:
        return decoded_bytes, None, audio_err or "Failed to extract audio track from video."

    return decoded_bytes, extracted_audio, None

def render_frutiger_video_player(video_bytes):
    """Render captured video preview in Frutiger Aero glass capsule pod."""
    if not video_bytes:
        return
    b64_video = base64.b64encode(video_bytes).decode()
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
      padding: 4px 0;
      overflow: hidden;
    }}
    .frutiger-video-pod {{
      width: 100%;
      max-width: 580px;
      background:
        radial-gradient(ellipse at 30% 8%, rgba(255,255,255,0.98), rgba(255,255,255,0.45) 40%, rgba(205,235,255,0.7) 75%),
        linear-gradient(155deg, rgba(245,252,255,0.95) 0%, rgba(195,228,255,0.85) 50%, rgba(145,198,245,0.9) 100%);
      border-radius: 36px;
      border: 2px solid rgba(255,255,255,0.95);
      box-shadow:
        0 14px 32px rgba(35,80,150,0.22),
        inset 0 3px 6px rgba(255,255,255,0.95),
        inset 0 -6px 14px rgba(40,100,190,0.18);
      padding: 14px 18px 16px 18px;
      position: relative;
      overflow: hidden;
    }}
    .frutiger-video-pod::before {{
      content: "";
      position: absolute;
      top: 0; left: 12%; right: 12%;
      height: 14px;
      background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0) 100%);
      border-radius: 0 0 50% 50%;
      pointer-events: none;
    }}
    .vid-header {{
      text-align: center;
      margin-bottom: 8px;
    }}
    .vid-title {{
      color: #104080;
      font-size: 12.5px;
      font-weight: 850;
      letter-spacing: 0.8px;
      text-shadow: 0 1px 0 rgba(255,255,255,0.9);
    }}
    .vid-sub {{
      color: #386ba8;
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 0.8px;
      margin-top: 1px;
    }}
    .video-viewport {{
      width: 100%;
      height: clamp(125px, 20vh, 175px);
      background: #06162a;
      border-radius: 18px;
      border: 2px solid rgba(255,255,255,0.85);
      box-shadow: inset 0 4px 12px rgba(0,0,0,0.6), 0 3px 8px rgba(30,70,140,0.18);
      overflow: hidden;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    video {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 16px;
    }}
    @media (max-height: 600px) and (orientation: landscape), (max-width: 600px) {{
      .frutiger-video-pod {{
        padding: 8px 12px 10px 12px;
        border-radius: 22px;
      }}
      .vid-title {{ font-size: 11px; }}
      .vid-sub {{ font-size: 8px; }}
      .video-viewport {{ height: 120px; }}
    }}
    </style>
    </head>
    <body>
    <div class="frutiger-video-pod">
      <div class="vid-header">
        <div class="vid-title">📹 CAPTURED VIDEO PLAYBACK</div>
        <div class="vid-sub">SYNCHRONIZED WEBCAM STREAM</div>
      </div>
      <div class="video-viewport">
        <video controls playsinline src="data:video/webm;base64,{b64_video}"></video>
      </div>
    </div>
    </body>
    </html>
    """
    st.components.v1.html(player_html, height=225)

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
    @media (max-height: 600px) and (orientation: landscape), (max-width: 600px) {{
      .frutiger-pod {{
        padding: 8px 12px 8px 12px;
        border-radius: 24px;
      }}
      .screen-wrapper {{
        margin-bottom: 6px;
        padding: 3px 6px;
      }}
      canvas {{
        height: 44px;
      }}
      .play-btn {{
        width: 38px;
        height: 38px;
      }}
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
    st.components.v1.html(player_html, height=220)

@st.cache_data(show_spinner=False)
def _analyze_audio_bytes_cached(raw_bytes: bytes) -> dict:
    import wave
    import io

    if not raw_bytes:
        return {
            "duration_seconds": 0.0,
            "average_amplitude": 0.0,
            "dominant_frequency_hz": 0.0,
            "samples": np.array([], dtype=np.float32),
            "sample_rate": 16000
        }

    # Fast path: in-memory RIFF/WAVE parsing (avoids disk I/O and FFmpeg subprocess entirely)
    is_wav = len(raw_bytes) > 12 and raw_bytes[:4] == b"RIFF" and raw_bytes[8:12] == b"WAVE"
    if is_wav:
        try:
            with wave.open(io.BytesIO(raw_bytes), "rb") as wav:
                n_channels = wav.getnchannels()
                sampwidth = wav.getsampwidth()
                sample_rate = wav.getframerate()
                frames = wav.readframes(wav.getnframes())

            if sampwidth == 2:
                samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
                if n_channels > 1:
                    samples = samples.reshape(-1, n_channels).mean(axis=1)

                duration = len(samples) / sample_rate if sample_rate > 0 else 0
                rms = np.sqrt(np.mean(samples ** 2)) if len(samples) > 0 else 0

                if len(samples) > 0:
                    spectrum = np.abs(np.fft.rfft(samples))
                    frequencies = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)
                    peak_frequency = frequencies[np.argmax(spectrum)]
                else:
                    peak_frequency = 0.0

                return {
                    "duration_seconds": round(duration, 2),
                    "average_amplitude": round(float(rms), 2),
                    "dominant_frequency_hz": round(float(peak_frequency), 1),
                    "samples": samples,
                    "sample_rate": sample_rate
                }
        except Exception:
            pass

    # Fallback path: use FFmpeg conversion for non-WAV formats (e.g. mp3/m4a uploads)
    input_path = None
    output_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".raw_audio") as temp:
            temp.write(raw_bytes)
            input_path = temp.name

        output_path = input_path + ".wav"
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with wave.open(output_path, "rb") as wav:
            frames = wav.readframes(wav.getnframes())
            sample_rate = wav.getframerate()

        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        duration = len(samples) / sample_rate if sample_rate > 0 else 0
        rms = np.sqrt(np.mean(samples ** 2)) if len(samples) > 0 else 0

        if len(samples) > 0:
            spectrum = np.abs(np.fft.rfft(samples))
            frequencies = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)
            peak_frequency = frequencies[np.argmax(spectrum)]
        else:
            peak_frequency = 0.0

        return {
            "duration_seconds": round(duration, 2),
            "average_amplitude": round(float(rms), 2),
            "dominant_frequency_hz": round(float(peak_frequency), 1),
            "samples": samples,
            "sample_rate": sample_rate
        }
    finally:
        if input_path and os.path.exists(input_path):
            try: os.remove(input_path)
            except Exception: pass
        if output_path and os.path.exists(output_path):
            try: os.remove(output_path)
            except Exception: pass

def analyze_audio(audio_file):
    if hasattr(audio_file, "seek"):
        audio_file.seek(0)
        raw_bytes = audio_file.read()
        audio_file.seek(0)
    elif isinstance(audio_file, bytes):
        raw_bytes = audio_file
    else:
        return {
            "duration_seconds": 0.0,
            "average_amplitude": 0.0,
            "dominant_frequency_hz": 0.0,
            "samples": np.array([], dtype=np.float32),
            "sample_rate": 16000
        }
    return _analyze_audio_bytes_cached(raw_bytes)

def check_cetacean_plausibility(evidence):
    """
    Lightweight heuristic to determine if recorded/uploaded audio contains
    a plausible cetacean-like acoustic signal (non-silent, high-frequency marine contour)
    vs silence or ambient room hum.
    """
    samples = evidence.get("samples")
    sample_rate = evidence.get("sample_rate", 16000)
    duration = evidence.get("duration_seconds", 0)
    rms = evidence.get("average_amplitude", 0)
    peak_freq = evidence.get("dominant_frequency_hz", 0)

    # 1. Minimum energy and duration check (rejects silence or brief accidental clicks)
    if rms < 65.0 or duration < 0.4:
        return False, "Signal energy below detection threshold (near silence)."

    if samples is None or len(samples) < 200:
        return False, "Insufficient audio frames for spectral analysis."

    # 2. Spectral Analysis (FFT)
    spectrum = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)

    total_power = float(np.sum(spectrum ** 2)) + 1e-9
    # Ambient low rumble band (< 350 Hz): AC hum, room rumble, desk thud
    rumble_power = float(np.sum(spectrum[freqs < 350] ** 2))
    # Marine whistling / burst-pulse band (750 Hz - 7500 Hz): phone playback / real cetacean sounds
    marine_band_power = float(np.sum(spectrum[(freqs >= 750) & (freqs <= 7500)] ** 2))

    rumble_ratio = rumble_power / total_power
    marine_ratio = marine_band_power / total_power

    # Plausibility condition:
    # Must not be pure low-frequency hum/rumble, and must exhibit either a dominant frequency >= 700 Hz
    # or significant energy in the typical cetacean whistling band (>= 18% of total spectral power).
    is_pure_rumble = (rumble_ratio > 0.85) and (peak_freq < 400)
    has_marine_energy = (peak_freq >= 700) or (marine_ratio >= 0.18)

    if not is_pure_rumble and has_marine_energy:
        return True, "Acoustic signature is consistent with cetacean spectral contour."
    else:
        return False, "Spectral profile lacks characteristic cetacean frequencies."

def render_live_status_badge(state, detail=None):
    if state == "Analysing":
        st.markdown("""
        <div class="live-status-pill status-analysing">
            <div class="badge-main"><span class="badge-icon">🔵</span> STATE: <strong>ANALYSING</strong></div>
            <div class="status-cycler-container">
                <div class="status-cycler-msg msg-1">Scanning acoustic signal…</div>
                <div class="status-cycler-msg msg-2">Mapping frequency contours…</div>
                <div class="status-cycler-msg msg-3">Checking cetacean plausibility…</div>
                <div class="status-cycler-msg msg-4">Decoding transmission…</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    badges = {
        "Idle": ("⚪", "IDLE", "STANDBY • MICROPHONE OFF", "status-idle"),
        "Listening": ("🔴", "LISTENING", "MICROPHONE ACTIVE • PLAY TRANSMISSION NEAR COMPUTER", "status-listening"),
        "Audio ready": ("🌊", "AUDIO READY", "RECORDING CAPTURED • READY FOR ANALYSIS", "status-ready"),
        "Analysing": ("🔵", "ANALYSING", "SPECTRAL DECODING & PLAUSIBILITY HEURISTIC...", "status-analysing"),
        "Signal rejected": ("⚠️", "SIGNAL REJECTED", "SOURCE APPEARS INSUFFICIENTLY CETACEOUS", "status-rejected"),
        "Translation complete": ("🟢", "TRANSLATION COMPLETE", "TRANSMISSION SYNTHESIZED SUCCESSFULLY", "status-complete")
    }
    icon, label, default_sub, css_class = badges.get(state, badges["Idle"])
    sub_text = detail or default_sub
    st.markdown(f"""
    <div class="live-status-pill {css_class}">
        <div class="badge-main"><span class="badge-icon">{icon}</span> STATE: <strong>{label}</strong></div>
        <div class="badge-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

def render_multimodal_status_badge(state, detail=None):
    if state == "Analysing":
        st.markdown("""
        <div class="live-status-pill status-analysing">
            <div class="badge-main"><span class="badge-icon">🔵</span> STATE: <strong>ANALYSING</strong></div>
            <div class="status-cycler-container">
                <div class="status-cycler-msg msg-1">Scanning acoustic signal…</div>
                <div class="status-cycler-msg msg-2">Mapping frequency contours…</div>
                <div class="status-cycler-msg msg-3">Checking cetacean plausibility…</div>
                <div class="status-cycler-msg msg-4">Decoding transmission…</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    badges = {
        "Idle": ("⚪", "IDLE", "STANDBY • CAMERA & MICROPHONE OFF", "status-idle"),
        "Capturing": ("🔴", "CAPTURING", "WEBCAM & MICROPHONE RECORDING • CLICK STOP WHEN FINISHED", "status-listening"),
        "Audio and video ready": ("🌊", "AUDIO + VIDEO READY", "MULTIMODAL CAPTURE STORED • READY FOR ANALYSIS", "status-ready"),
        "Analysing": ("🔵", "ANALYSING", "SPECTRAL DECODING & PLAUSIBILITY HEURISTIC...", "status-analysing"),
        "Signal rejected": ("⚠️", "SIGNAL REJECTED", "SOURCE APPEARS INSUFFICIENTLY CETACEOUS", "status-rejected"),
        "Translation complete": ("🟢", "TRANSLATION COMPLETE", "TRANSMISSION SYNTHESIZED SUCCESSFULLY", "status-complete")
    }
    icon, label, default_sub, css_class = badges.get(state, badges["Idle"])
    sub_text = detail or default_sub
    st.markdown(f"""
    <div class="live-status-pill {css_class}">
        <div class="badge-main"><span class="badge-icon">{icon}</span> STATE: <strong>{label}</strong></div>
        <div class="badge-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

def render_signal_rejected_card():
    st.markdown("""
    <div class="signal-rejected-card">
        <div class="rejected-title">SIGNAL REJECTED.</div>
        <div class="rejected-sub">SOURCE APPEARS INSUFFICIENTLY CETACEOUS.</div>
        <div class="rejected-status">AWAITING A MORE MARINE TRANSMISSION...</div>
    </div>
    """, unsafe_allow_html=True)

def render_multimodal_error_card(message="MEDIA DECODING ERROR. UNABLE TO PARSE CAPTURED STREAM."):
    st.markdown(f"""
    <div class="signal-rejected-card" style="padding: 16px 20px; margin: 12px auto; max-width: 500px;">
        <div class="rejected-title" style="font-size: 1.05rem;">CAPTURE PROCESSING ERROR</div>
        <div class="rejected-sub" style="font-size: 0.85rem;">{message}</div>
        <div class="rejected-status" style="font-size: 0.72rem;">PLEASE RETRY CAPTURE WHEN READY</div>
    </div>
    """, unsafe_allow_html=True)

def render_cockpit_header():
    """Render top telemetry header with LED indicator, system title, and real status."""
    st.markdown("""
    <div class="cockpit-header-bar">
        <div class="cockpit-logo-row">
            <span class="cockpit-icon">🐬</span>
            <div>
                <div class="cockpit-title">CETACEAN INTERFACE</div>
                <div class="cockpit-subtitle">COCKPIT v2.4 • BIOACOUSTIC TRANSLATION</div>
            </div>
        </div>
        <div class="header-right">
            <div class="cockpit-status-pill">
                <span class="led-dot green-pulsing"></span>
                <span>SYSTEM ONLINE</span>
            </div>
            <div class="telemetry-pill">
                <div class="signal-bars"><span></span><span></span><span></span><span></span></div>
                <span>LOCAL AI</span>
            </div>
            <div class="battery-pill">
                <span class="battery-bar"><span class="battery-fill"></span></span>
                <span>READY</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_system_telemetry(input_mode, has_audio):
    """Render real system telemetry chips (no fake scientific data)."""
    mode_name = input_mode.replace("🎥 ", "").replace("🎙️ ", "").replace("📁 ", "")
    audio_tag = "ACTIVE (AUDIO READY)" if has_audio else "STANDBY"
    st.markdown(f"""
    <div class="system-telemetry-row">
        <div class="env-chip"><span class="chip-dot"></span>INPUT: {mode_name}</div>
        <div class="env-chip"><span class="chip-dot"></span>HYDROPHONE: 16.0 kHz MONO</div>
        <div class="env-chip"><span class="chip-dot"></span>LOCAL LLM: GEMMA 3-4B</div>
        <div class="env-chip"><span class="chip-dot"></span>SIGNAL: {audio_tag}</div>
    </div>
    """, unsafe_allow_html=True)

def render_panel_header(title, tag):
    """Render glossy section pill header for cockpit panels."""
    st.markdown(f"""
    <div class="panel-section-header">
        <div class="panel-led"></div>
        <div class="panel-title">{title}</div>
        <div class="panel-tag">{tag}</div>
    </div>
    """, unsafe_allow_html=True)

def render_standby_spectrogram_card():
    """Render standby radar animation and message before acoustic signal exists."""
    st.markdown("""
    <div class="standby-spectrogram-pod">
        <div class="spec-header-row">
            <div class="spec-led-green"></div>
            <div class="spec-title">ACOUSTIC SPECTROGRAM</div>
            <div class="spec-tabs">
                <span class="spec-tab active">REALTIME</span>
                <span class="spec-tab">SPECTRAL</span>
            </div>
        </div>
        <div class="spec-screen-viewport">
            <div class="radar-grid"></div>
            <div class="radar-scanline"></div>
            <div class="standby-spec-text-row">
                <span>📡</span> AWAITING ACOUSTIC TRANSMISSION...
            </div>
            <div class="standby-spec-sub">PASSIVE HYDROPHONE LISTENING • 16.0 kHz MONO</div>
        </div>
        <div class="spec-metrics-placeholder">
            <div class="metric-chip">DURATION: -- s</div>
            <div class="metric-chip">PEAK FREQ: -- Hz</div>
            <div class="metric-chip">AMPLITUDE: --</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_interpretation_card(text):
    """Render interpreted dialogue in a Frutiger Aero glass capsule pod."""
    if not text:
        return
    escaped_text = html.escape(text).replace("\n", "<br>")
    st.markdown(f"""
    <div class="interpretation-bubble-pod">
        <div class="interp-header-row">
            <div class="dolphin-emblem">🐬</div>
            <div class="interp-title-col">
                <div class="interp-tag">INTERPRETED TRANSMISSION</div>
                <div class="interp-sub">LOCAL GEMMA 3-4B SYNTHESIS</div>
            </div>
            <div class="confidence-badge">CONFIDENCE: LOW</div>
        </div>
        <div class="interp-quote-box">
            <div class="quote-text">{escaped_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_floating_dock():
    """Render bottom navigation dock matching cockpit aesthetic."""
    st.markdown("""
    <div class="floating-dock-container">
        <div class="floating-dock">
            <div class="dock-item active"><span class="dock-icon">🏠</span> COCKPIT</div>
            <div class="dock-item"><span class="dock-icon">📡</span> HYDROPHONE</div>
            <div class="dock-item"><span class="dock-icon">💬</span> TRANSLATION</div>
            <div class="dock-item"><span class="dock-icon">⚙️</span> SETTINGS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def _generate_signal_graph_cached(samples_bytes: bytes, sample_rate: int) -> bytes:
    import io
    samples = np.frombuffer(samples_bytes, dtype=np.float32)
    if len(samples) == 0:
        return b""

    spectrum = np.abs(np.fft.rfft(samples))
    frequencies = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)

    if HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(7, 2.6), facecolor="none")
        ax.set_facecolor("#06152a")

        ax.plot(frequencies, spectrum, color="#00f0ff", linewidth=1.6, label="Frequency Contour")
        ax.fill_between(frequencies, spectrum, color="#0088cc", alpha=0.32)

        ax.set_xlim(0, min(sample_rate / 2, 8000))
        ax.set_xlabel("Frequency (Hz)", color="#79c5e8", fontsize=8, fontweight="bold")
        ax.set_ylabel("Amplitude", color="#79c5e8", fontsize=8, fontweight="bold")
        ax.set_title("Frequency Contour & Spectrum", color="#00e5ff", fontsize=9, fontweight="bold", pad=4)

        ax.tick_params(colors="#79c5e8", labelsize=7)
        ax.grid(True, color="#10365c", linestyle="--", linewidth=0.6)

        for spine in ax.spines.values():
            spine.set_color("#205080")
            spine.set_linewidth(1.0)

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    else:
        # High-definition PIL fallback matching dark ocean theme
        w, h = 640, 220
        img = Image.new("RGB", (w, h), color=(6, 21, 42))
        draw = ImageDraw.Draw(img)

        # Draw grid
        for x in range(50, w - 20, 70):
            draw.line([(x, 30), (x, h - 35)], fill=(16, 54, 92), width=1)
        for y in range(40, h - 35, 35):
            draw.line([(50, y), (w - 20, y)], fill=(16, 54, 92), width=1)

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
            draw.polygon(poly, fill=(0, 60, 120))
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i+1]], fill=(0, 240, 255), width=2)

        # Outer border & Labels
        draw.rectangle([(50, 30), (w - 20, h - 35)], outline=(32, 80, 128), width=1)
        draw.text((w // 2 - 90, 10), "Frequency Contour & Spectrum", fill=(0, 229, 255))
        draw.text((w // 2 - 35, h - 22), "Frequency (Hz)", fill=(121, 197, 232))
        draw.text((8, h // 2 - 10), "Amp", fill=(121, 197, 232))

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()

def generate_signal_graph(samples, sample_rate):
    """Render dark ocean spectrogram plot with glowing cyan contour."""
    if len(samples) == 0:
        return None
    samples_bytes = samples.tobytes() if hasattr(samples, "tobytes") else bytes(samples)
    img_bytes = _generate_signal_graph_cached(samples_bytes, sample_rate)
    if img_bytes:
        st.image(img_bytes)
    return img_bytes

def process_cetacean_translation(evidence, images, duration_val, word_limit):
    """Run Gemma 3 interpretation and ElevenLabs TTS for plausible cetacean signal."""
    try:
        response = ollama.chat(
            model="gemma3:4b",
            keep_alive="1h",
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
        except Exception:
            st.session_state.tts_audio = None

    except Exception as e:
        st.error(f"MODEL CONNECTION ERROR: {e}")

render_cockpit_header()

col_obs, col_sig = st.columns([1, 1], gap="medium")

with col_obs:
    render_panel_header("LIVE OBSERVATION", "OPTICAL & HYDROPHONE FEED")

    input_mode = st.radio(
        "SIGNAL SOURCE",
        ["🎥 LIVE MULTIMODAL CAPTURE", "🎙️ LIVE TRANSLATION", "📁 UPLOAD RECORDING"],
        horizontal=True,
        label_visibility="collapsed",
        key="acoustic_signal_mode"
    )

    if "last_signal_mode" not in st.session_state:
        st.session_state.last_signal_mode = input_mode
    elif st.session_state.last_signal_mode != input_mode:
        st.session_state.last_signal_mode = input_mode
        st.session_state.multimodal_error = None
        st.session_state.live_rejected = False
        st.session_state.upload_rejected = False

    active_audio = None
    is_multimodal_mode = (input_mode == "🎥 LIVE MULTIMODAL CAPTURE")
    is_live_mode = (input_mode == "🎙️ LIVE TRANSLATION")

    if is_multimodal_mode:
        # 1. Live Multimodal Capture
        # Flow: START CAPTURE → capture mic + webcam → STOP CAPTURE → AUDIO/VIDEO READY → ANALYSE SIGNAL
        multimodal_data = multimodal_capture_component(key="multimodal_recorder_widget")
        if multimodal_data and isinstance(multimodal_data, dict):
            if multimodal_data.get("action") == "started":
                st.session_state.multimodal_state = "Capturing"
                st.session_state.multimodal_error = None
            elif multimodal_data.get("data_url") or multimodal_data.get("video_base64"):
                ts = multimodal_data.get("timestamp")
                if ts != st.session_state.get("last_multimodal_hash"):
                    st.session_state.last_multimodal_hash = ts
                    raw_payload = multimodal_data.get("data_url") or multimodal_data.get("video_base64")
                    video_bytes, extracted_audio, err = process_captured_media_payload(raw_payload)

                    if video_bytes and extracted_audio:
                        st.session_state.captured_video = video_bytes
                        st.session_state.captured_audio = extracted_audio
                        st.session_state.multimodal_state = "Audio and video ready"
                        st.session_state.multimodal_rejected = False
                        st.session_state.multimodal_error = None
                        st.session_state.interpretation = None
                        st.session_state.tts_audio = None
                    else:
                        if video_bytes:
                            st.session_state.captured_video = video_bytes
                        else:
                            st.session_state.captured_video = None
                        st.session_state.captured_audio = None
                        st.session_state.multimodal_error = err or "Media capture processing failed."

        multimodal_status_placeholder = st.empty()
        with multimodal_status_placeholder:
            render_multimodal_status_badge(st.session_state.multimodal_state)

        if st.session_state.get("multimodal_error"):
            render_multimodal_error_card(st.session_state.multimodal_error)

        if st.session_state.captured_audio and st.session_state.captured_video:
            active_audio = io.BytesIO(st.session_state.captured_audio)
            render_frutiger_video_player(st.session_state.captured_video)
            render_frutiger_recording_player(active_audio)
        else:
            active_audio = None

    elif is_live_mode:
        # 1. Live Audio Capture
        # Flow: START LISTENING → RECORD → STOP → AUDIO READY → ANALYSE SIGNAL → ANALYSING → PLAUSIBILITY CHECK → TRANSLATION
        try:
            live_audio = st.audio_input(
                "START LISTENING (CLICK MIC TO RECORD) • CLICK AGAIN TO STOP",
                key="live_audio_mic_input"
            )
        except Exception as mic_err:
            st.error(f"MICROPHONE PERMISSION / ACCESS ERROR: {mic_err}")
            live_audio = None

        if live_audio is not None:
            raw_bytes = live_audio.getvalue()
            audio_hash = hashlib.md5(raw_bytes).hexdigest()
            st.session_state.live_recorded_audio = live_audio

            # New recording captured: transition to Audio ready (do NOT automatically analyse)
            if st.session_state.get("live_audio_hash") != audio_hash:
                st.session_state.live_audio_hash = audio_hash
                st.session_state.live_state = "Audio ready"
                st.session_state.interpretation = None
                st.session_state.tts_audio = None
                st.session_state.live_rejected = False

            active_audio = live_audio
            render_frutiger_recording_player(active_audio)
        else:
            # Idle or currently recording
            st.session_state.live_recorded_audio = None
            st.session_state.live_audio_hash = None
            st.session_state.live_state = "Idle"
            st.session_state.live_rejected = False
            active_audio = None

        live_status_placeholder = st.empty()
        with live_status_placeholder:
            render_live_status_badge(st.session_state.live_state)

    else:
        # Upload Recording Mode
        audio_file = st.file_uploader(
            "Upload a cetacean recording",
            type=["wav", "mp3", "m4a"],
            key="upload_audio_input"
        )
        if audio_file is not None:
            active_audio = audio_file
            render_frutiger_recording_player(active_audio)

with col_sig:
    render_panel_header("ACOUSTIC SIGNAL & TELEMETRY", "HYDROPHONE ARRAY")

    if active_audio:
        evidence = analyze_audio(active_audio)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "DURATION",
                f'{evidence["duration_seconds"]} s'
            )

        with col2:
            st.metric(
                "PEAK FREQ",
                f'{evidence["dominant_frequency_hz"]} Hz'
            )

        with col3:
            st.metric(
                "AMPLITUDE",
                f'{evidence["average_amplitude"]}'
            )

        generate_signal_graph(evidence["samples"], evidence["sample_rate"])

        images = []

        if is_multimodal_mode:
            # LIVE MULTIMODAL CAPTURE PIPELINE
            # Sequence: START CAPTURE → STOP CAPTURE → AUDIO/VIDEO READY → ANALYSE SIGNAL
            status_placeholder = st.empty()
            is_analysing = (st.session_state.multimodal_state == "Analysing")
            analyse_clicked = st.button(
                "ANALYSE SIGNAL",
                disabled=is_analysing,
                key="multimodal_analyse_signal_btn"
            )

            if analyse_clicked:
                st.session_state.multimodal_state = "Analysing"
                with multimodal_status_placeholder:
                    render_multimodal_status_badge("Analysing")
                status_placeholder.markdown(render_analysing_status(), unsafe_allow_html=True)
                with st.spinner("DECODING CETACEAN TRANSMISSION..."):
                    is_plausible, reason = check_cetacean_plausibility(evidence)
                    if is_plausible:
                        st.session_state.multimodal_rejected = False
                        duration_val = evidence["duration_seconds"]
                        word_limit = get_speech_length_guideline(duration_val)
                        # For now, video is capture/storage/preview only. Do NOT add visual AI analysis.
                        process_cetacean_translation(evidence, [], duration_val, word_limit)
                        st.session_state.multimodal_state = "Translation complete"
                        with multimodal_status_placeholder:
                            render_multimodal_status_badge("Translation complete")
                    else:
                        st.session_state.multimodal_rejected = True
                        st.session_state.multimodal_state = "Signal rejected"
                        st.session_state.interpretation = None
                        st.session_state.tts_audio = None
                        with multimodal_status_placeholder:
                            render_multimodal_status_badge("Signal rejected")
                status_placeholder.empty()

            if st.session_state.get("multimodal_rejected"):
                render_signal_rejected_card()

        elif is_live_mode:
            # LIVE TRANSLATION PIPELINE
            # Sequence: START LISTENING → RECORD → STOP → AUDIO READY → ANALYSE SIGNAL → ANALYSING → PLAUSIBILITY CHECK → TRANSLATION
            status_placeholder = st.empty()
            is_analysing = (st.session_state.live_state == "Analysing")
            analyse_clicked = st.button(
                "ANALYSE SIGNAL",
                disabled=is_analysing,
                key="live_analyse_signal_btn"
            )

            if analyse_clicked:
                st.session_state.live_state = "Analysing"
                with live_status_placeholder:
                    render_live_status_badge("Analysing")
                status_placeholder.markdown(render_analysing_status(), unsafe_allow_html=True)
                with st.spinner("DECODING CETACEAN TRANSMISSION..."):
                    is_plausible, reason = check_cetacean_plausibility(evidence)
                    if is_plausible:
                        st.session_state.live_rejected = False
                        duration_val = evidence["duration_seconds"]
                        word_limit = get_speech_length_guideline(duration_val)
                        process_cetacean_translation(evidence, images, duration_val, word_limit)
                        st.session_state.live_state = "Translation complete"
                        with live_status_placeholder:
                            render_live_status_badge("Translation complete")
                    else:
                        st.session_state.live_rejected = True
                        st.session_state.live_state = "Signal rejected"
                        st.session_state.interpretation = None
                        st.session_state.tts_audio = None
                        with live_status_placeholder:
                            render_live_status_badge("Signal rejected")
                status_placeholder.empty()

            if st.session_state.get("live_rejected"):
                render_signal_rejected_card()

        else:
            # UPLOAD RECORDING PIPELINE
            status_placeholder = st.empty()
            if st.button("ANALYSE SIGNAL", key="upload_analyse_signal_btn"):
                status_placeholder.markdown(render_analysing_status(), unsafe_allow_html=True)
                with st.spinner("DECODING CETACEAN TRANSMISSION..."):
                    is_plausible, reason = check_cetacean_plausibility(evidence)
                    if is_plausible:
                        st.session_state.upload_rejected = False
                        duration_val = evidence["duration_seconds"]
                        word_limit = get_speech_length_guideline(duration_val)
                        process_cetacean_translation(evidence, images, duration_val, word_limit)
                    else:
                        st.session_state.upload_rejected = True
                        st.session_state.interpretation = None
                        st.session_state.tts_audio = None
                status_placeholder.empty()

            if st.session_state.get("upload_rejected"):
                render_signal_rejected_card()

        if st.session_state.interpretation:
            render_interpretation_card(st.session_state.interpretation)
            if st.session_state.get("tts_audio"):
                render_frutiger_audio_player(st.session_state.tts_audio)

    else:
        # Awaiting acoustic signal (standby radar)
        render_standby_spectrogram_card()
        st.button("ANALYSE SIGNAL", disabled=True, key="standby_analyse_signal_btn")

# Real system telemetry chips and bottom navigation dock
render_system_telemetry(input_mode, active_audio is not None)
render_floating_dock()

st.markdown("""
<div class="session-status-block">
    <div class="status-item">LOCAL MODEL: GEMMA 3-4B</div>
    <div class="status-item">CONNECTION: LOCAL</div>
    <div class="status-item">HYDROPHONE: REALTIME 16kHz MONO</div>
</div>
""", unsafe_allow_html=True)

with st.expander("🔑 ELEVENLABS SETTINGS", expanded=not bool(os.environ.get("ELEVENLABS_API_KEY"))):
    if os.environ.get("ELEVENLABS_API_KEY"):
        st.success("🟢 ElevenLabs API Key is active")
    else:
        st.info("⚪ ElevenLabs Key not detected (Audio synthesis requires ElevenLabs API key)")

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