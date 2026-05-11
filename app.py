"""
╔══════════════════════════════════════════════════╗
║           HyperPilot v1.0                       ║
║       AI-Powered HyperOS Device Agent           ║
╚══════════════════════════════════════════════════╝
"""

import streamlit as st
import time
import os
import sys
import json
from datetime import datetime
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from adb_controller import ADBController, DeviceInfo
from agent import HyperPilotAgent, AgentMode, AgentResponse

# ─── Page Config ────────────────────────────────────────────────

st.set_page_config(
    page_title="HyperPilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "# 🚀 HyperPilot — AI Device Agent\nControl your Android device with natural language.",
    },
)

# ─── Custom CSS ─────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&display=swap');

    :root {
        --bg-primary: #06080f;
        --bg-secondary: #0c1020;
        --bg-card: rgba(12, 16, 32, 0.8);
        --border: #1a2040;
        --accent: #00f0ff;
        --accent-dim: #00a8b3;
        --accent-glow: rgba(0, 240, 255, 0.4);
        --accent2: #a855f7;
        --accent2-glow: rgba(168, 85, 247, 0.4);
        --accent3: #f43f5e;
        --success: #00ff88;
        --warning: #ffaa00;
        --error: #ff3366;
        --text-primary: #e8edf5;
        --text-secondary: #7a8baa;
        --text-muted: #3a4565;
        --neon-cyan: 0 0 10px rgba(0,240,255,0.5), 0 0 20px rgba(0,240,255,0.3), 0 0 40px rgba(0,240,255,0.1);
        --neon-purple: 0 0 10px rgba(168,85,247,0.5), 0 0 20px rgba(168,85,247,0.3), 0 0 40px rgba(168,85,247,0.1);
        --neon-green: 0 0 10px rgba(0,255,136,0.5), 0 0 20px rgba(0,255,136,0.3);
    }

    /* ═══ MAIN BACKGROUND ═══ */
    .stApp {
        background: #06080f;
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(0,240,255,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(244,63,94,0.02) 0%, transparent 50%);
    }

    /* Grid overlay */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            linear-gradient(rgba(0,240,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,240,255,0.02) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
    }

    /* Scanline effect */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0,0,0,0.03) 2px,
            rgba(0,0,0,0.03) 4px
        );
        pointer-events: none;
        z-index: 1;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* ═══ HERO SECTION ═══ */
    .hero-container {
        text-align: center;
        padding: 2rem 0 1rem 0;
        position: relative;
        z-index: 2;
    }

    .hero-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(0,240,255,0.5));
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f0ff 0%, #a855f7 40%, #f43f5e 70%, #00f0ff 100%);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease-in-out infinite;
        margin-bottom: 0;
        letter-spacing: 6px;
        text-shadow: none;
        filter: drop-shadow(0 0 30px rgba(0,240,255,0.3));
    }

    .hero-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #4a5a7a;
        letter-spacing: 8px;
        text-transform: uppercase;
        margin-top: 0.3rem;
    }

    .hero-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #5a6a8a;
        margin-top: 0.8rem;
        font-weight: 300;
    }

    .hero-tagline span {
        color: #00f0ff;
        font-weight: 500;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 300% center; }
    }

    /* ═══ NEON STATUS BAR ═══ */
    .neon-status-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 0.8rem 1.5rem;
        margin: 1rem auto;
        max-width: 700px;
        background: rgba(10, 14, 30, 0.9);
        border: 1px solid rgba(0,240,255,0.15);
        border-radius: 50px;
        box-shadow: 0 0 30px rgba(0,240,255,0.05), inset 0 0 30px rgba(0,0,0,0.3);
    }

    .neon-status-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 1px;
    }

    .neon-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        animation: neonPulse 2s infinite;
    }

    .neon-dot.green { background: #00ff88; box-shadow: 0 0 8px #00ff88, 0 0 16px rgba(0,255,136,0.3); }
    .neon-dot.yellow { background: #ffaa00; box-shadow: 0 0 8px #ffaa00, 0 0 16px rgba(255,170,0,0.3); }
    .neon-dot.red { background: #ff3366; box-shadow: 0 0 8px #ff3366, 0 0 16px rgba(255,51,102,0.3); }
    .neon-dot.cyan { background: #00f0ff; box-shadow: 0 0 8px #00f0ff, 0 0 16px rgba(0,240,255,0.3); }

    @keyframes neonPulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 8px currentColor; }
        50% { opacity: 0.6; box-shadow: 0 0 4px currentColor; }
    }

    .status-label { color: #4a5a7a; }
    .status-value { color: #e8edf5; font-weight: 600; }
    .status-value.green { color: #00ff88; }
    .status-value.cyan { color: #00f0ff; }

    /* ═══ GLASSMORPHISM CARDS ═══ */
    .glass-card {
        background: rgba(12, 16, 32, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(0,240,255,0.08);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.6rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,240,255,0.3), transparent);
    }

    .glass-card:hover {
        border-color: rgba(0,240,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 30px rgba(0,240,255,0.05);
        transform: translateY(-2px);
    }

    .glass-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6rem;
        color: #3a5070;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 4px;
    }

    .glass-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #e8edf5;
    }

    .glass-value.green { color: #00ff88; text-shadow: 0 0 20px rgba(0,255,136,0.3); }
    .glass-value.cyan { color: #00f0ff; text-shadow: 0 0 20px rgba(0,240,255,0.3); }
    .glass-value.purple { color: #a855f7; text-shadow: 0 0 20px rgba(168,85,247,0.3); }
    .glass-value.yellow { color: #ffaa00; text-shadow: 0 0 20px rgba(255,170,0,0.3); }
    .glass-value.red { color: #ff3366; text-shadow: 0 0 20px rgba(255,51,102,0.3); }

    /* ═══ COMMAND INPUT (TERMINAL STYLE) ═══ */
    .terminal-input-frame {
        background: rgba(6, 8, 15, 0.9);
        border: 1px solid rgba(0,240,255,0.12);
        border-radius: 16px;
        padding: 0;
        margin: 1.5rem 0;
        overflow: hidden;
        box-shadow: 0 4px 40px rgba(0,0,0,0.4), 0 0 60px rgba(0,240,255,0.03);
    }

    .terminal-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.6rem 1rem;
        background: rgba(15, 20, 40, 0.8);
        border-bottom: 1px solid rgba(0,240,255,0.08);
    }

    .terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
    .terminal-dot.red { background: #ff5f57; }
    .terminal-dot.yellow { background: #febc2e; }
    .terminal-dot.green { background: #28c840; }

    .terminal-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #3a5070;
        margin-left: 8px;
        letter-spacing: 1px;
    }

    .terminal-body {
        padding: 1rem 1.2rem;
    }

    .terminal-prompt {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #00f0ff;
        margin-bottom: 0.5rem;
    }

    .terminal-prompt span { color: #3a5070; }

    /* ═══ QUICK ACTION BUTTONS ═══ */
    .quick-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 6px;
        margin: 0.8rem 0;
    }

    /* ═══ LOG ENTRIES ═══ */
    .log-entry {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: rgba(10, 14, 28, 0.7);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        position: relative;
        overflow: hidden;
    }

    .log-entry::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
    }

    .log-entry.success::before { background: #00ff88; box-shadow: 0 0 10px rgba(0,255,136,0.3); }
    .log-entry.error::before { background: #ff3366; box-shadow: 0 0 10px rgba(255,51,102,0.3); }
    .log-entry.info::before { background: #00f0ff; box-shadow: 0 0 10px rgba(0,240,255,0.3); }
    .log-entry.warning::before { background: #ffaa00; box-shadow: 0 0 10px rgba(255,170,0,0.3); }

    .log-time { color: #2a3555; font-size: 0.65rem; min-width: 55px; }
    .log-action { color: #00f0ff; }
    .log-result { color: #7a8baa; }

    /* ═══ THINKING ANIMATION ═══ */
    .thinking {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, rgba(0,240,255,0.05), rgba(168,85,247,0.05));
        border: 1px solid rgba(0,240,255,0.12);
        border-radius: 12px;
        margin: 0.5rem 0;
    }

    .thinking-dots span {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #00f0ff;
        animation: dotBounce 1.4s infinite ease-in-out both;
        box-shadow: 0 0 6px #00f0ff;
    }
    .thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
    .thinking-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes dotBounce {
        0%, 80%, 100% { transform: scale(0.3); opacity: 0.3; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ═══ DIVIDERS ═══ */
    .futuristic-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(0,240,255,0.15) 20%, rgba(168,85,247,0.2) 50%, rgba(0,240,255,0.15) 80%, transparent 100%);
        margin: 1.5rem 0;
    }

    .divider-glow {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00f0ff, #a855f7, #00f0ff, transparent);
        margin: 2rem 0;
        opacity: 0.4;
    }

    /* ═══ SIDEBAR ═══ */
    section[data-testid="stSidebar"] {
        background: #080c18 !important;
        border-right: 1px solid rgba(0,240,255,0.08) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #7a8baa;
    }

    /* ═══ STREAMLIT OVERRIDES ═══ */
    .stTextInput > div > div > input {
        background: rgba(6, 8, 15, 0.9) !important;
        border: 1px solid rgba(0,240,255,0.15) !important;
        border-radius: 12px !important;
        color: #e8edf5 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1rem !important;
        padding: 0.9rem 1.3rem !important;
        transition: all 0.3s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 20px rgba(0,240,255,0.1), inset 0 0 20px rgba(0,240,255,0.02) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #2a3555 !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #00f0ff, #0080aa) !important;
        color: #06080f !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        padding: 0.6rem 1.8rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        box-shadow: 0 0 20px rgba(0,240,255,0.2) !important;
        transition: all 0.3s !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 30px rgba(0,240,255,0.4), 0 0 60px rgba(0,240,255,0.1) !important;
        transform: translateY(-2px) !important;
    }

    /* Secondary buttons (quick actions) */
    .stButton > button:not([kind="primary"]) {
        background: rgba(12, 16, 32, 0.6) !important;
        color: #7a8baa !important;
        border: 1px solid rgba(0,240,255,0.08) !important;
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        padding: 0.4rem 0.5rem !important;
        transition: all 0.3s !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(0,240,255,0.3) !important;
        color: #00f0ff !important;
        background: rgba(0,240,255,0.05) !important;
        box-shadow: 0 0 15px rgba(0,240,255,0.1) !important;
    }

    /* Radio buttons */
    .stRadio > div {
        gap: 0.3rem !important;
    }

    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #06080f; }
    ::-webkit-scrollbar-thumb { background: #1a2040; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2a3555; }

    /* ═══ SECTION HEADERS ═══ */
    h3 {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.85rem !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: #5a7a9a !important;
    }

    /* ═══ EXPANDER ═══ */
    .streamlit-expanderHeader {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        color: #00f0ff !important;
    }

    /* ═══ SUCCESS/WARNING/ERROR BOXES ═══ */
    .stAlert > div {
        background: rgba(12, 16, 32, 0.8) !important;
        border: 1px solid rgba(0,240,255,0.1) !important;
        border-radius: 10px !important;
    }

    /* ═══ FOOTER ═══ */
    .cyber-footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        position: relative;
        z-index: 2;
    }

    .cyber-footer-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6rem;
        color: #1a2540;
        letter-spacing: 4px;
        text-transform: uppercase;
    }

    .cyber-footer-line {
        width: 200px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,240,255,0.2), transparent);
        margin: 0.8rem auto;
    }

    /* ═══ METRICS ROW ═══ */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 1rem 0;
    }

    .metric-box {
        text-align: center;
        padding: 0.8rem;
        background: rgba(10, 14, 28, 0.6);
        border: 1px solid rgba(0,240,255,0.06);
        border-radius: 10px;
    }

    .metric-number {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #00f0ff;
        text-shadow: 0 0 15px rgba(0,240,255,0.3);
    }

    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.55rem;
        color: #3a5070;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 2px;
    }

    /* ═══ DEMO MODE BANNER ═══ */
    .demo-banner {
        background: linear-gradient(135deg, rgba(255,170,0,0.08), rgba(255,170,0,0.02));
        border: 1px solid rgba(255,170,0,0.15);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .demo-banner-icon {
        font-size: 1.2rem;
    }

    .demo-banner-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #cc8800;
    }

    .demo-banner-sub {
        font-size: 0.65rem;
        color: #664400;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State ──────────────────────────────────────────────

if "adb" not in st.session_state:
    st.session_state.adb = ADBController()
if "agent" not in st.session_state:
    st.session_state.agent = HyperPilotAgent(st.session_state.adb)
if "device_info" not in st.session_state:
    st.session_state.device_info = None
if "log_history" not in st.session_state:
    st.session_state.log_history = []
if "command_count" not in st.session_state:
    st.session_state.command_count = 0
if "connected" not in st.session_state:
    st.session_state.connected = False
if "screenshot_path" not in st.session_state:
    st.session_state.screenshot_path = None

adb: ADBController = st.session_state.adb
agent: HyperPilotAgent = st.session_state.agent


# ─── Helper Functions ───────────────────────────────────────────

def add_log(action: str, result: str, status: str = "info"):
    """Add entry to command log."""
    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": action,
        "result": result,
        "status": status,
    }
    st.session_state.log_history.append(entry)
    # Keep last 50
    if len(st.session_state.log_history) > 50:
        st.session_state.log_history = st.session_state.log_history[-50:]


def refresh_device_info():
    """Refresh connected device information."""
    try:
        info = adb.get_device_info()
        st.session_state.device_info = info
        st.session_state.connected = info.connected
        return info
    except Exception as e:
        st.session_state.connected = False
        return None


def check_adb():
    """Check if ADB is available."""
    import shutil
    return shutil.which("adb") is not None


# ─── Hero Header ────────────────────────────────────────────────

st.markdown("""
<div class="hero-container">
    <div class="hero-icon">⚡</div>
    <div class="hero-title">HYPERPILOT</div>
    <div class="hero-subtitle">AI-Powered HyperOS Device Agent</div>
    <div class="hero-tagline">Control your Android device with <span>natural language</span></div>
</div>
""", unsafe_allow_html=True)

# Neon status bar
st.markdown("""
<div class="neon-status-bar">
    <div class="neon-status-item">
        <span class="neon-dot cyan"></span>
        <span class="status-label">SYSTEM</span>
        <span class="status-value cyan">ONLINE</span>
    </div>
    <div class="neon-status-item">
        <span class="neon-dot green"></span>
        <span class="status-label">AI ENGINE</span>
        <span class="status-value green">READY</span>
    </div>
    <div class="neon-status-item">
        <span class="neon-dot yellow"></span>
        <span class="status-label">MODE</span>
        <span class="status-value">DEMO</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)


# ─── ADB Check ──────────────────────────────────────────────────
# ─── ADB Check ──────────────────────────────────────────────────
# Demo mode toggle
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

ADB_AVAILABLE = check_adb()
DEVICE_CONNECTED = False

if ADB_AVAILABLE:
    # ADB exists, but check if device is actually connected
    try:
        import subprocess
        _r = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        _lines = [l for l in _r.stdout.strip().split("\n")[1:] if l.strip() and "device" in l and "offline" not in l]
        DEVICE_CONNECTED = len(_lines) > 0
    except Exception:
        DEVICE_CONNECTED = False

if not ADB_AVAILABLE or not DEVICE_CONNECTED:
    # No ADB or no device → demo mode
    if not ADB_AVAILABLE:
        msg = "⚠️ ADB not found — <strong>Demo Mode Active</strong>"
        sub = "Install Android platform-tools for real device control."
    else:
        msg = "📱 No device connected — <strong>Demo Mode Active</strong>"
        sub = "Connect via USB/WiFi ADB for live control. Commands are simulated."
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.05));
                border: 1px solid rgba(245,158,11,0.3); border-radius: 12px;
                padding: 1rem 1.5rem; margin-bottom: 1rem;">
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #f59e0b;">
            {msg}
            <br><span style="font-size: 0.7rem; color: #92400e;">
            {sub}
            </span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.demo_mode = True
else:
    st.session_state.demo_mode = False


# ─── Sidebar ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 1.8rem; margin-bottom: 4px; filter: drop-shadow(0 0 10px rgba(0,240,255,0.5));">⚡</div>
        <div style="font-family: 'Orbitron'; font-weight: 800; font-size: 1.1rem; color: #00f0ff; letter-spacing: 3px; text-shadow: 0 0 15px rgba(0,240,255,0.3);">HYPERPILOT</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #2a3555; letter-spacing: 3px; margin-top: 4px;">v1.0.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)

    # Device Connection
    st.markdown("### 📱 Device")

    if st.session_state.demo_mode:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">Mode</div>
            <div class="status-value warning">🎭 Demo</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Connect a device via ADB to go live")
    else:
        if st.button("🔍 Detect Device", use_container_width=True):
            with st.spinner("Scanning for devices..."):
                result = adb.check_connection()
                if result.success:
                    info = refresh_device_info()
                    if info and info.connected:
                        st.success(f"Connected: {info.model}")
                        add_log("Device Connect", f"{info.model} ({info.serial})", "success")
                    else:
                        st.error("No device found")
                else:
                    st.error(result.error)

    if st.session_state.connected and st.session_state.device_info:
        info = st.session_state.device_info
        st.markdown(f"""
        <div class="status-card">
            <div class="status-label">Device</div>
            <div class="status-value">{info.model or 'Unknown'}</div>
        </div>
        <div class="status-card">
            <div class="status-label">Android</div>
            <div class="status-value">{info.android_version} (SDK {info.sdk_version})</div>
        </div>
        <div class="status-card">
            <div class="status-label">Screen</div>
            <div class="status-value">{info.screen_size[0]}×{info.screen_size[1]}</div>
        </div>
        <div class="status-card">
            <div class="status-label">Battery</div>
            <div class="status-value {'connected' if info.battery_level > 20 else 'warning'}">{info.battery_level}%</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card">
            <div class="status-label">Status</div>
            <div class="status-value error">No Device</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)

    # Stats
    st.markdown("### 📊 Stats")
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">Commands Executed</div>
        <div class="status-value" style="color: #8b5cf6;">{st.session_state.command_count}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)

    # ADB Mode
    st.markdown("### ⚙️ Mode")
    st.radio(
        "Command Parser",
        ["🧠 Local (Rule-based)", "🤖 AI (OpenAI)"],
        index=0,
        key="mode_select",
        label_visibility="collapsed",
    )

    if st.button("🗑️ Clear Log", use_container_width=True):
        st.session_state.log_history = []
        st.rerun()

    # Manual ADB
    st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)
    st.markdown("### 🔧 Manual ADB")
    manual_cmd = st.text_input("Shell command", placeholder="e.g. getprop ro.product.model", key="manual_adb")
    if manual_cmd and st.button("▶️ Run", use_container_width=True):
        result = adb.shell(manual_cmd)
        if result.success:
            st.code(result.output)
            add_log(f"Manual: {manual_cmd}", result.output[:100], "success")
        else:
            st.error(result.error)
            add_log(f"Manual: {manual_cmd}", result.error, "error")


# ─── Main Content ───────────────────────────────────────────────

# Status bar
conn_status = "🟢 Connected" if st.session_state.connected else "🔴 Disconnected"
conn_color = "connected" if st.session_state.connected else "error"

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
    <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #64748b; letter-spacing: 1px;">
        STATUS: <span style="color: {'#10b981' if st.session_state.connected else '#ef4444'};">{'ONLINE' if st.session_state.connected else 'OFFLINE'}</span>
    </span>
    <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #475569;">
        {datetime.now().strftime('%H:%M:%S')}
    </span>
</div>
""", unsafe_allow_html=True)


# ─── Command Input ──────────────────────────────────────────────

st.markdown("### 💬 Command")

# Quick actions row
quick_actions = agent.get_quick_actions()
cols = st.columns(7)
for i, qa in enumerate(quick_actions[:7]):
    with cols[i]:
        if st.button(qa["label"], key=f"qa_{i}", use_container_width=True):
            st.session_state["pending_command"] = qa["command"]

# Second row
cols2 = st.columns(7)
for i, qa in enumerate(quick_actions[7:14]):
    with cols2[i]:
        if st.button(qa["label"], key=f"qa_{i+7}", use_container_width=True):
            st.session_state["pending_command"] = qa["command"]

# Main command input
st.markdown("")
command = st.text_input(
    "Enter command",
    placeholder='e.g. "open youtube", "go home", "search lofi music on youtube"',
    key="command_input",
    label_visibility="collapsed",
)

# Check if a quick action was clicked → auto-execute
if "pending_command" in st.session_state:
    command = st.session_state.pop("pending_command")
    execute = True
else:
    execute = False

# Action buttons (only check Execute if no quick action triggered)
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2, 1, 1, 1])

with btn_col1:
    if not execute:
        execute = st.button("⚡ Execute Command", type="primary", use_container_width=True)

with btn_col2:
    if st.button("📷 Screenshot", use_container_width=True):
        with st.spinner("Capturing..."):
            result = adb.screenshot("/tmp/hyperpilot_ss.png")
            if result.success:
                st.session_state.screenshot_path = result.output
                add_log("Screenshot", "Captured", "success")
            else:
                add_log("Screenshot", result.error, "error")

# ─── Execute Command ────────────────────────────────────────────

if execute and command:
    st.session_state.command_count += 1

    # Thinking animation
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("""
    <div class="thinking">
        <div class="thinking-dots">
            <span></span><span></span><span></span>
        </div>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #06b6d4;">
            Processing command...
        </span>
    </div>
    """, unsafe_allow_html=True)

    # DEMO MODE: simulate response
    if st.session_state.demo_mode:
        time.sleep(0.5)  # Simulate processing
        from agent import CommandParser
        _parser = CommandParser()
        _actions = _parser.parse(command)
        _flat = []
        for _a in _actions:
            if isinstance(_a, list):
                _flat.extend(_a)
            else:
                _flat.append(_a)

        if _flat:
            _descriptions = [a.description for a in _flat if a.description]
            resp_text = f"✅ [DEMO] {' → '.join(_descriptions) if _descriptions else 'Command parsed successfully'}"
            st.success(resp_text)
            add_log(command, resp_text, "success")
            st.caption(f"⏱️ ~50ms • {len(_flat)} step(s) • 🎭 Demo Mode")
            with st.expander("🧠 Agent Reasoning (Demo)", expanded=True):
                for i, a in enumerate(_flat, 1):
                    st.markdown(f"**Step {i}:** ✅ {a.description or a.action_type}")
                    st.code(f"adb shell ... ({a.action_type})", language="bash")
        else:
            st.warning(f"🤔 [DEMO] Can't parse: '{command}'")
            add_log(command, "Unrecognized command", "warning")
    else:
        # REAL MODE: process with ADB
        response: AgentResponse = agent.process_command(command)
        thinking_placeholder.empty()

        if response.success:
            st.success(response.final_result)
            add_log(command, response.final_result, "success")
        else:
            st.warning(response.final_result)
            add_log(command, response.final_result, "warning")

        st.caption(f"⏱️ {response.execution_time_ms:.0f}ms • {len(response.steps)} step(s)")

        if response.steps:
            with st.expander("🧠 Agent Reasoning", expanded=False):
                for i, step in enumerate(response.steps, 1):
                    status = "✅" if step.result and step.result.success else "❌"
                    cmd = step.result.command if step.result else "?"
                    ms = f" ({step.result.duration_ms:.0f}ms)" if step.result else ""
                    st.markdown(f"**Step {i}:** {status} {step.thought}{ms}")
                    st.code(cmd, language="bash")

    thinking_placeholder.empty()

elif execute and not command:
    st.info("Type a command first! Try: `open youtube` or `go home`")


# ─── Screenshot Display ─────────────────────────────────────────

if st.session_state.screenshot_path and os.path.exists(st.session_state.screenshot_path):
    st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)
    st.markdown("### 📱 Device Screen")
    st.image(st.session_state.screenshot_path, use_container_width=True, caption="Latest Screenshot")


# ─── Command Log ────────────────────────────────────────────────

st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)
st.markdown("### 📋 Command Log")

if st.session_state.log_history:
    for entry in reversed(st.session_state.log_history[-20:]):
        status_class = entry["status"]
        status_icon = {"success": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}.get(status_class, "•")
        st.markdown(f"""
        <div class="log-entry {status_class}">
            <span class="log-time">{entry['time']}</span>
            {status_icon}
            <span class="log-action">{entry['action']}</span>
            →
            <span class="log-result">{entry['result']}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #475569; font-family: 'JetBrains Mono'; font-size: 0.85rem;">
        No commands yet. Try: <code style="color: #06b6d4;">open youtube</code>
    </div>
    """, unsafe_allow_html=True)


# ─── Footer ─────────────────────────────────────────────────────

st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="cyber-footer">
    <div class="cyber-footer-line"></div>
    <div class="cyber-footer-text">
        HYPERPILOT v1.0 &nbsp;•&nbsp; AI DEVICE AGENT &nbsp;•&nbsp; BUILT FOR HACKATHONS
    </div>
    <div class="cyber-footer-line"></div>
</div>
""", unsafe_allow_html=True)


# ─── Auto-refresh timer (subtle) ───────────────────────────────

# Update clock every second
st.markdown("""
<script>
    // Update time display
    setInterval(function() {
        const elements = document.querySelectorAll('[data-testid="stMarkdownContainer"]');
    }, 1000);
</script>
""", unsafe_allow_html=True)
