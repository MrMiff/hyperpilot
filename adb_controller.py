"""
HyperPilot — ADB Controller
Low-level ADB interaction layer for HyperOS/Android devices.
"""

import subprocess
import json
import time
import re
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    HOME = "home"
    BACK = "back"
    RECENT = "recent"
    POWER = "power"
    TAP = "tap"
    SWIPE = "swipe"
    TYPE_TEXT = "type_text"
    OPEN_APP = "open_app"
    Screenshot = "screenshot"
    SCREEN_RECORD = "screen_record"
    KEY_EVENT = "key_event"
    SHELL = "shell"
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    serial: str = ""
    model: str = ""
    android_version: str = ""
    sdk_version: str = ""
    screen_size: Tuple[int, int] = (0, 0)
    connected: bool = False
    screen_on: bool = True
    current_app: str = ""
    battery_level: int = 0


@dataclass
class ADBResult:
    success: bool
    output: str
    error: str = ""
    command: str = ""
    duration_ms: float = 0.0


@dataclass
class DeviceSnapshot:
    screenshot_path: str = ""
    ocr_text: str = ""
    current_activity: str = ""
    timestamp: float = 0.0
    ui_elements: List[Dict] = field(default_factory=list)


class ADBController:
    """Manages ADB connections and commands for HyperOS devices."""

    # Common HyperOS / MIUI / Android app packages
    APP_PACKAGES = {
        "settings": "com.android.settings",
        "youtube": "com.google.android.youtube",
        "chrome": "com.android.chrome",
        "camera": "com.android.camera",
        "gallery": "com.miui.gallery",
        "photos": "com.google.android.apps.photos",
        "whatsapp": "com.whatsapp",
        "instagram": "com.instagram.android",
        "twitter": "com.twitter.android",
        "telegram": "org.telegram.messenger",
        "maps": "com.google.android.apps.maps",
        "clock": "com.android.deskclock",
        "calculator": "com.miui.calculator",
        "calendar": "com.android.calendar",
        "contacts": "com.android.contacts",
        "phone": "com.android.dialer",
        "messages": "com.android.mms",
        "files": "com.mi.android.globalFileexplorer",
        "music": "com.miui.player",
        "weather": "com.miui.weather2",
        "notes": "com.miui.notes",
        "security": "com.miui.securitycenter",
        "themes": "com.android.thememanager",
        "appstore": "com.xiaomi.market",
        "playstore": "com.android.vending",
        "drive": "com.google.android.apps.docs",
        "gmail": "com.google.android.gm",
        "docs": "com.google.android.apps.docs.editors.docs",
        "sheets": "com.google.android.apps.docs.editors.sheets",
        "slides": "com.google.android.apps.docs.editors.slides",
        "meet": "com.google.android.apps.tachyon",
        "zoom": "us.zoom.videomeetings",
        "spotify": "com.spotify.music",
        "netflix": "com.netflix.mediaclient",
        "browser": "com.android.browser",
        "aiassistant": "com.xiaomi.aiasst.service",
        "mihome": "com.xiaomi.smarthome",
        "filesgoogle": "com.google.android.apps.nbu.files",
    }

    # ADB Key codes
    KEY_CODES = {
        "home": 3,
        "back": 4,
        "recent": 187,
        "power": 26,
        "volume_up": 24,
        "volume_down": 25,
        "enter": 66,
        "delete": 67,
        "tab": 61,
        "space": 62,
        "menu": 82,
    }

    def __init__(self, device_serial: Optional[str] = None, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.device_serial = device_serial
        self.device_info = DeviceInfo()
        self._last_screenshot: Optional[str] = None

    def _build_cmd(self, *args) -> List[str]:
        """Build ADB command with optional device serial."""
        cmd = [self.adb_path]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        cmd.extend(args)
        return cmd

    def _run(self, *args, timeout: int = 15) -> ADBResult:
        """Execute an ADB command and return structured result."""
        cmd = self._build_cmd(*args)
        cmd_str = " ".join(cmd)
        start = time.time()

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            duration = (time.time() - start) * 1000
            output = proc.stdout.strip()
            error = proc.stderr.strip()

            # ADB sometimes prints to stderr even on success
            if proc.returncode == 0 or (output and not error):
                return ADBResult(
                    success=True, output=output, command=cmd_str, duration_ms=duration
                )
            else:
                return ADBResult(
                    success=False,
                    output=output,
                    error=error or "Command failed",
                    command=cmd_str,
                    duration_ms=duration,
                )
        except subprocess.TimeoutExpired:
            return ADBResult(
                success=False,
                error=f"Command timed out after {timeout}s",
                command=cmd_str,
                duration_ms=timeout * 1000,
            )
        except FileNotFoundError:
            return ADBResult(
                success=False,
                error="ADB not found. Install Android platform-tools.",
                command=cmd_str,
            )
        except Exception as e:
            return ADBResult(
                success=False, error=str(e), command=cmd_str
            )

    # ─── Device Management ───────────────────────────────────────

    def check_connection(self) -> ADBResult:
        """Check if any device is connected."""
        result = self._run("devices", "-l")
        if result.success:
            lines = result.output.split("\n")
            devices = [
                l for l in lines[1:] if l.strip() and "device" in l and "offline" not in l
            ]
            if devices:
                # Parse serial from first device
                first = devices[0].split()[0]
                if not self.device_serial:
                    self.device_serial = first
                result.output = f"{len(devices)} device(s) connected"
                result.success = True
            else:
                result.success = False
                result.error = "No devices connected. Check USB/WiFi ADB."
        return result

    def get_device_info(self) -> DeviceInfo:
        """Gather comprehensive device information."""
        info = DeviceInfo(serial=self.device_serial or "")

        if not self.device_serial:
            conn = self.check_connection()
            if not conn.success:
                return info

        # Model
        r = self._run("shell", "getprop", "ro.product.model")
        info.model = r.output if r.success else "Unknown"

        # Android version
        r = self._run("shell", "getprop", "ro.build.version.release")
        info.android_version = r.output if r.success else "?"

        # SDK version
        r = self._run("shell", "getprop", "ro.build.version.sdk")
        info.sdk_version = r.output if r.success else "?"

        # Screen size
        r = self._run("shell", "wm", "size")
        if r.success and "x" in r.output:
            try:
                size_str = r.output.split(":")[-1].strip()
                w, h = size_str.split("x")
                info.screen_size = (int(w), int(h))
            except Exception:
                pass

        # Battery
        r = self._run("shell", "dumpsys", "battery")
        if r.success:
            match = re.search(r"level:\s*(\d+)", r.output)
            if match:
                info.battery_level = int(match.group(1))

        # Screen state
        r = self._run("shell", "dumpsys", "power")
        if r.success:
            info.screen_on = "mHoldingDisplaySuspendBlocker=true" in r.output

        # Current activity
        r = self._run(
            "shell",
            "dumpsys",
            "activity",
            "activities",
        )
        if r.success:
            match = re.search(r"mResumedActivity.*\{.*\s(\S+)/(\S+)", r.output)
            if match:
                info.current_app = match.group(1)

        info.connected = True
        self.device_info = info
        return info

    def list_devices(self) -> List[str]:
        """List all connected devices."""
        result = self._run("devices")
        devices = []
        if result.success:
            for line in result.output.split("\n")[1:]:
                if line.strip() and "device" in line:
                    serial = line.split("\t")[0]
                    devices.append(serial)
        return devices

    # ─── Screen Control ──────────────────────────────────────────

    def tap(self, x: int, y: int) -> ADBResult:
        """Tap at screen coordinates."""
        return self._run("shell", "input", "tap", str(x), str(y))

    def swipe(
        self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300
    ) -> ADBResult:
        """Swipe from (x1,y1) to (x2,y2)."""
        return self._run(
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration_ms),
        )

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> ADBResult:
        """Long press at coordinates."""
        return self.swipe(x, y, x, y, duration_ms)

    def type_text(self, text: str) -> ADBResult:
        """Type text on device. Escapes special characters."""
        escaped = text.replace(" ", "%s").replace("&", "\\&").replace("<", "\\<").replace(">", "\\>")
        return self._run("shell", "input", "text", escaped)

    def press_key(self, key: str) -> ADBResult:
        """Press a named key or numeric key code."""
        if key.lower() in self.KEY_CODES:
            code = self.KEY_CODES[key.lower()]
            return self._run("shell", "input", "keyevent", str(code))
        # Try as raw keycode number
        try:
            int(key)
            return self._run("shell", "input", "keyevent", key)
        except ValueError:
            return ADBResult(success=False, error=f"Unknown key: {key}")

    def home(self) -> ADBResult:
        """Press Home button."""
        return self.press_key("home")

    def back(self) -> ADBResult:
        """Press Back button."""
        return self.press_key("back")

    def recents(self) -> ADBResult:
        """Open recent apps."""
        return self.press_key("recent")

    def power(self) -> ADBResult:
        """Toggle screen power."""
        return self.press_key("power")

    def volume_up(self) -> ADBResult:
        return self.press_key("volume_up")

    def volume_down(self) -> ADBResult:
        return self.press_key("volume_down")

    def wake_screen(self) -> ADBResult:
        """Turn screen on if off."""
        info = self.get_device_info()
        if not info.screen_on:
            self.power()
            time.sleep(0.3)
            # Swipe up to unlock
            if info.screen_size != (0, 0):
                w, h = info.screen_size
                self.swipe(w // 2, h * 3 // 4, w // 2, h // 4, 200)
        return ADBResult(success=True, output="Screen woken")

    # ─── App Control ─────────────────────────────────────────────

    def open_app(self, package_or_name: str) -> ADBResult:
        """Open an app by package name or friendly name."""
        # Try friendly name lookup
        name_lower = package_or_name.lower().strip()
        package = self.APP_PACKAGES.get(name_lower, package_or_name)

        # Use monkey to launch (more reliable than am start for cold launch)
        result = self._run("shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1")
        if not result.success:
            # Fallback: try am start
            result = self._run(
                "shell", "am", "start", "-n", f"{package}/.MainActivity"
            )
        if result.success:
            result.output = f"Opened {name_lower} ({package})"
        return result

    def close_app(self, package: str) -> ADBResult:
        """Force stop an app."""
        return self._run("shell", "am", "force-stop", package)

    def get_running_apps(self) -> List[str]:
        """List running app packages."""
        result = self._run("shell", "dumpsys", "activity", "activities")
        apps = []
        if result.success:
            for match in re.finditer(r"TaskRecord.*?A=(\S+)", result.output):
                apps.append(match.group(1))
        return list(set(apps))

    # ─── Screenshot & OCR ────────────────────────────────────────

    def screenshot(self, local_path: str = "/tmp/hyperpilot_screen.png") -> ADBResult:
        """Capture device screenshot."""
        remote_path = "/sdcard/hyperpilot_screen.png"
        # Take screenshot on device
        result = self._run("shell", "screencap", "-p", remote_path)
        if result.success:
            # Pull to local
            result = self._run("pull", remote_path, local_path)
            if result.success:
                self._last_screenshot = local_path
                result.output = local_path
                # Cleanup remote
                self._run("shell", "rm", remote_path)
        return result

    def get_screen_text(self) -> str:
        """Get current foreground activity as text context."""
        result = self._run("shell", "dumpsys", "window", "windows")
        if result.success:
            match = re.search(r"mCurrentFocus.*Window\{.*\s(\S+)\}", result.output)
            if match:
                return match.group(1)
        return ""

    # ─── Shell Commands ──────────────────────────────────────────

    def shell(self, command: str) -> ADBResult:
        """Run arbitrary shell command."""
        return self._run("shell", command)

    def install_apk(self, apk_path: str) -> ADBResult:
        """Install an APK."""
        return self._run("install", "-r", apk_path, timeout=120)

    def get_prop(self, prop: str) -> str:
        """Get system property."""
        result = self._run("shell", "getprop", prop)
        return result.output if result.success else ""

    # ─── Bulk Operations ─────────────────────────────────────────

    def execute_macro(self, actions: List[Dict]) -> List[ADBResult]:
        """Execute a sequence of actions (macro)."""
        results = []
        for action in actions:
            action_type = action.get("type", "")
            params = action.get("params", {})

            if action_type == "tap":
                results.append(self.tap(params.get("x", 0), params.get("y", 0)))
            elif action_type == "swipe":
                results.append(
                    self.swipe(
                        params.get("x1", 0), params.get("y1", 0),
                        params.get("x2", 0), params.get("y2", 0),
                        params.get("duration", 300),
                    )
                )
            elif action_type == "type":
                results.append(self.type_text(params.get("text", "")))
            elif action_type == "key":
                results.append(self.press_key(params.get("key", "home")))
            elif action_type == "open":
                results.append(self.open_app(params.get("app", "")))
            elif action_type == "wait":
                time.sleep(params.get("seconds", 1))
                results.append(ADBResult(success=True, output="Waited"))
            elif action_type == "shell":
                results.append(self.shell(params.get("cmd", "")))
            else:
                results.append(
                    ADBResult(success=False, error=f"Unknown action: {action_type}")
                )

            # Small delay between actions for stability
            if action_type != "wait":
                time.sleep(0.1)

        return results

    def __repr__(self) -> str:
        return f"ADBController(serial={self.device_serial}, connected={self.device_info.connected})"
