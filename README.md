<div align="center">

# 🚀 HyperPilot

### AI-Powered HyperOS Device Agent

**Control your Android device with natural language commands.**

---

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![ADB](https://img.shields.io/badge/ADB-Android-3DDC84?style=flat-square&logo=android&logoColor=white)](https://developer.android.com/tools/adb)
[![License: MIT](https://img.shields.io/badge/License-MIT-06b6d4?style=flat-square)](LICENSE)
[![Hackathon](https://img.shields.io/badge/🏆-Hackathon%20Ready-8b5cf6?style=flat-square)](#-quick-start)

<br>

```
  ╔═══════════════════════════════════════════════╗
  ║  "Open YouTube"     → 📺 YouTube launches     ║
  ║  "Go home"          → 🏠 Home screen          ║
  ║  "Search lofi..."   → 🔍 YouTube search        ║
  ║  "Type hello"       → ⌨️  Text appears          ║
  ╚═══════════════════════════════════════════════╝
```

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Control** | Type commands like "open youtube" — no syntax needed |
| 🏠 **App Launching** | Open any app by name: YouTube, Chrome, WhatsApp, etc. |
| 📱 **Device Automation** | Tap, swipe, type, scroll — full screen control |
| 🔍 **AI Command Parsing** | Rule-based + optional OpenAI integration |
| 🎨 **Futuristic UI** | Dark mode, glowing accents, terminal vibes |
| 📊 **Action Logs** | Full audit trail of every command executed |
| 📷 **Screenshot Capture** | Grab device screen with one click |
| ⚡ **Quick Actions** | One-tap buttons for common operations |
| 🧩 **Multi-Step Workflows** | Chain actions: "search lofi on youtube" |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HyperPilot UI                         │
│               (Streamlit • Dark Mode)                    │
├─────────────────┬───────────────────────────────────────┤
│   Command Box   │         Quick Actions                  │
│  "open youtube" │  🏠 Home  ◀️ Back  📱 Recent  ...      │
├─────────────────┴───────────────────────────────────────┤
│                    Agent Layer                           │
│           (NLP Parser → Action Planning)                 │
│    "open youtube" → [{type: open, app: youtube}]        │
├─────────────────────────────────────────────────────────┤
│                  ADB Controller                          │
│          (subprocess → Android Debug Bridge)             │
│       adb shell monkey -p com.google.android.youtube 1  │
├─────────────────────────────────────────────────────────┤
│                  Android Device                          │
│              (HyperOS / MIUI / AOSP)                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **ADB** ([install guide](https://developer.android.com/tools/adb))
- **Android device** with USB Debugging enabled

### 1. Enable USB Debugging on your phone

1. Go to **Settings → About Phone**
2. Tap **MIUI Version** 7 times (enables Developer Options)
3. Go to **Settings → Additional Settings → Developer Options**
4. Enable **USB Debugging**
5. Connect via USB and accept the RSA prompt

### 2. Install HyperPilot

```bash
git clone https://github.com/yourusername/hyperpilot.git
cd hyperpilot
pip install -r requirements.txt
```

### 3. Verify ADB connection

```bash
adb devices
# Should show your device serial number
```

### 4. Launch HyperPilot

```bash
streamlit run app.py
```

Open **http://localhost:8501** — start commanding your device! 🎉

---

## 💡 Usage Examples

### Basic Commands

```bash
# Navigation
"go home"                    → Press home button
"go back"                    → Press back button
"recent apps"                → Open multitasking view

# App Control
"open youtube"               → Launch YouTube
"open settings"              → Launch Settings
"open chrome"                → Launch Chrome
"open whatsapp"              → Launch WhatsApp
"open camera"                → Launch Camera

# Text Input
"type hello world"           → Type "hello world"
"type 'search query'"        → Type search query

# Screen Control
"scroll down"                → Swipe up (scroll content down)
"scroll up"                  → Swipe down (scroll content up)
"tap 540 1000"               → Tap at coordinates (540, 1000)
"swipe 500 1500 500 500"     → Swipe gesture

# Volume
"volume up"                  → Increase volume
"volume down"                → Decrease volume

# Multi-step
"search lofi music on youtube" → Open YouTube → Tap search → Type query → Enter
```

### Quick Action Buttons

The UI includes one-tap buttons for the most common operations:

| Button | Action |
|--------|--------|
| 🏠 Home | Navigate to home screen |
| ◀️ Back | Press back button |
| 📱 Recent | Show recent apps |
| 📸 Screenshot | Capture device screen |
| 🔧 Settings | Open device settings |
| 📺 YouTube | Launch YouTube |
| 🌐 Chrome | Launch Chrome browser |
| 📷 Camera | Open camera app |
| 💬 WhatsApp | Launch WhatsApp |
| 🎵 Spotify | Open Spotify |
| ⬆️ Vol Up | Increase volume |
| ⬇️ Vol Down | Decrease volume |
| 🔄 Scroll Down | Scroll page down |
| ⬆️ Scroll Up | Scroll page up |

---

## 📁 Project Structure

```
hyperpilot/
├── app.py              # Streamlit UI — main entry point
├── adb_controller.py   # ADB command layer — device control
├── agent.py            # AI agent — NLP command parser
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── assets/             # Screenshots, diagrams
```

---

## 🔧 Configuration

### Environment Variables (Optional)

```bash
# For AI-powered command parsing
export OPENAI_API_KEY="sk-..."

# For custom ADB path
export ADB_PATH="/usr/local/bin/adb"
```

### Supported Devices

HyperPilot works with any Android device that supports ADB:

- ✅ Xiaomi / Redmi / POCO (HyperOS / MIUI)
- ✅ Google Pixel (Stock Android)
- ✅ Samsung (One UI)
- ✅ OnePlus (OxygenOS)
- ✅ Any AOSP-based ROM

---

## 🗺️ Roadmap

### v1.0 (Current — MVP)
- [x] ADB device connection
- [x] Natural language command parsing
- [x] App launching, navigation, text input
- [x] Futuristic Streamlit UI
- [x] Quick action buttons
- [x] Command execution logs
- [x] Screenshot capture

### v1.1 (Coming Soon)
- [ ] OCR screen text detection (pytesseract)
- [ ] AI reasoning with OpenAI function calling
- [ ] Multi-step workflow builder
- [ ] Custom command macros
- [ ] WiFi ADB support

### v2.0 (Future)
- [ ] Computer vision — tap by element description ("tap the search button")
- [ ] Voice command input (Whisper + streaming)
- [ ] Screen mirroring with scrcpy integration
- [ ] Macro recorder (record + replay touch sequences)
- [ ] Plugin system for custom actions
- [ ] Multi-device management dashboard

---

## 🧪 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI** | Streamlit | Web-based dashboard |
| **Backend** | Python 3.11 | Core logic |
| **ADB** | subprocess | Android device control |
| **NLP** | Regex + OpenAI | Command parsing |
| **OCR** | Tesseract (optional) | Screen text detection |
| **Design** | Custom CSS | Futuristic dark theme |

---

## 🤝 Contributing

Contributions welcome! This is a hackathon project — fork it, improve it, make it yours.

```bash
# 1. Fork the repo
# 2. Create your feature branch
git checkout -b feature/amazing-feature

# 3. Commit your changes
git commit -m "Add amazing feature"

# 4. Push to the branch
git push origin feature/amazing-feature

# 5. Open a Pull Request
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [ADB Documentation](https://developer.android.com/tools/adb)
- [Streamlit](https://streamlit.io) — amazing rapid prototyping
- [Android Open Source Project](https://source.android.com)
- Built with ❤️ for AI Hackathons

---

<div align="center">

**Made for hackathons. Built for demos. Ready to win.** 🏆

</div>
