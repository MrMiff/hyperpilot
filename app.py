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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a1f2e;
        --border: #1e293b;
        --accent: #06b6d4;
        --accent-glow: rgba(6, 182, 212, 0.3);
        --accent2: #8b5cf6;
        --accent2-glow: rgba(139, 92, 246, 0.3);
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #475569;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #0f172a 50%, #0a0e17 100%);
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #06b6d4, #8b5cf6, #06b6d4);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease-in-out infinite;
        margin-bottom: 0;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #64748b;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 200% center; }
    }

    /* Status cards */
    .status-card {
        background: linear-gradient(135deg, #1a1f2e, #111827);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }

    .status-card:hover {
        border-color: #06b6d4;
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.1);
    }

    .status-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .status-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #f1f5f9;
    }

    .status-value.connected { color: #10b981; }
    .status-value.warning { color: #f59e0b; }
    .status-value.error { color: #ef4444; }

    /* Pulse animation for connected */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    .pulse-dot.green { background: #10b981; }
    .pulse-dot.red { background: #ef4444; }
    .pulse-dot.yellow { background: #f59e0b; }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }

    /* Command input */
    .command-input-container {
        background: linear-gradient(135deg, #1a1f2e, #111827);
        border: 2px solid #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: border-color 0.3s;
    }

    .command-input-container:focus-within {
        border-color: #06b6d4;
        box-shadow: 0 0 30px rgba(6, 182, 212, 0.15);
    }

    /* Quick action buttons */
    .quick-btn {
        background: linear-gradient(135deg, #1e293b, #111827);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.5rem 0.8rem;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;
    }
    .quick-btn:hover {
        border-color: #06b6d4;
        color: #06b6d4;
        background: rgba(6, 182, 212, 0.1);
        transform: translateY(-1px);
    }

    /* Log entries */
    .log-entry {
        background: #111827;
        border-left: 3px solid #1e293b;
        border-radius: 0 8px 8px 0;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }

    .log-entry.success { border-left-color: #10b981; }
    .log-entry.error { border-left-color: #ef4444; }
    .log-entry.info { border-left-color: #06b6d4; }
    .log-entry.warning { border-left-color: #f59e0b; }

    .log-time {
        color: #475569;
        font-size: 0.7rem;
    }

    .log-action {
        color: #06b6d4;
    }

    .log-result {
        color: #94a3b8;
    }

    /* Thinking animation */
    .thinking {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(6, 182, 212, 0.2);
        border-radius: 12px;
        margin: 0.5rem 0;
    }

    .thinking-dots span {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #06b6d4;
        animation: dotBounce 1.4s infinite ease-in-out both;
    }
    .thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
    .thinking-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes dotBounce {
        0%, 80%, 100% { transform: scale(0.4); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Divider */
    .futuristic-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #1e293b, #06b6d4, #1e293b, transparent);
        margin: 1.5rem 0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid #1e293b;
    }

    /* Override Streamlit input */
    .stTextInput > div > div > input {
        background: #0f172a !important;
        border: 2px solid #1e293b !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1rem !important;
        padding: 0.8rem 1.2rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #06b6d4 !important;
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.15) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4, #0891b2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.3) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }

    /* Custom columns */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #111827);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .metric-card .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #06b6d4;
    }
    .metric-card .metric-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
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
    <div class="hero-title">HyperPilot</div>
    <div class="hero-subtitle">AI-Powered HyperOS Device Agent</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)


# ─── ADB Check ──────────────────────────────────────────────────

if not check_adb():
    st.error("⚠️ **ADB not found.** Install Android platform-tools and ensure it's in your PATH.")
    st.code("""
# macOS (Homebrew)
brew install android-platform-tools

# Ubuntu/Debian
sudo apt install adb

# Windows: Download from https://developer.android.com/studio/releases/platform-tools
    """, language="bash")
    st.stop()


# ─── Sidebar ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 1.5rem; font-weight: 700; color: #06b6d4;">🚀</div>
        <div style="font-family: 'Inter'; font-weight: 600; color: #f1f5f9;">HyperPilot</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #475569; letter-spacing: 2px;">v1.0.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="futuristic-divider">', unsafe_allow_html=True)

    # Device Connection
    st.markdown("### 📱 Device")

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

# Check if a quick action was clicked
if "pending_command" in st.session_state:
    command = st.session_state.pop("pending_command")

# Action buttons
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2, 1, 1, 1])

with btn_col1:
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

    # Process
    response: AgentResponse = agent.process_command(command)
    thinking_placeholder.empty()

    # Show result
    if response.success:
        st.success(response.final_result)
        add_log(command, response.final_result, "success")
    else:
        st.warning(response.final_result)
        add_log(command, response.final_result, "warning")

    # Show execution time
    st.caption(f"⏱️ {response.execution_time_ms:.0f}ms • {len(response.steps)} step(s)")

    # Show reasoning
    if response.steps:
        with st.expander("🧠 Agent Reasoning", expanded=False):
            for i, step in enumerate(response.steps, 1):
                status = "✅" if step.result and step.result.success else "❌"
                cmd = step.result.command if step.result else "?"
                ms = f" ({step.result.duration_ms:.0f}ms)" if step.result else ""
                st.markdown(f"**Step {i}:** {status} {step.thought}{ms}")
                st.code(cmd, language="bash")

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
<div style="text-align: center; padding: 0.5rem 0 1rem 0;">
    <span style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #334155; letter-spacing: 2px;">
        HYPERPILOT v1.0 • AI DEVICE AGENT • BUILT FOR HACKATHONS
    </span>
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
