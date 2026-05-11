"""
HyperPilot — AI Agent
Natural language command parser and action executor.
Routes user intent → ADB actions.
"""

import re
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from adb_controller import ADBController, ADBResult, ActionType


class AgentMode(Enum):
    LOCAL = "local"        # Rule-based parsing (no API needed)
    AI = "ai"              # OpenAI-powered parsing


@dataclass
class AgentAction:
    """Single parsed action to execute."""
    action_type: str
    params: Dict = field(default_factory=dict)
    description: str = ""
    confidence: float = 1.0


@dataclass
class AgentStep:
    """A step in the agent's reasoning."""
    thought: str = ""
    action: Optional[AgentAction] = None
    result: Optional[ADBResult] = None
    timestamp: float = 0.0


@dataclass
class AgentResponse:
    """Full agent response for a command."""
    command: str
    parsed_actions: List[AgentAction] = field(default_factory=list)
    steps: List[AgentStep] = field(default_factory=list)
    final_result: str = ""
    success: bool = False
    execution_time_ms: float = 0.0
    reasoning: str = ""


class CommandParser:
    """Rule-based natural language command parser."""

    # Intent patterns → action mapping
    INTENT_PATTERNS = [
        # Navigation
        {
            "patterns": [r"\bgo\s*(to\s*)?home\b", r"\bhome\s*screen\b", r"\bpress\s*home\b", r"\breturn\s*home\b"],
            "action": "key",
            "params": {"key": "home"},
            "description": "Navigate to home screen",
        },
        {
            "patterns": [r"\bgo\s*back\b", r"\bpress\s*back\b", r"\bback\s*button\b", r"\breturn\b"],
            "action": "key",
            "params": {"key": "back"},
            "description": "Press back button",
        },
        {
            "patterns": [r"\brecent\s*apps?\b", r"\bshow\s*multitask\b", r"\bswitch\s*app\b"],
            "action": "key",
            "params": {"key": "recent"},
            "description": "Open recent apps",
        },
        {
            "patterns": [r"\block\s*(screen|phone|device)\b", r"\bturn\s*off\s*screen\b"],
            "action": "key",
            "params": {"key": "power"},
            "description": "Toggle screen power",
        },

        # App launching
        {
            "patterns": [r"\bopen\s+youtube\b", r"\blaunch\s+youtube\b", r"\byoutube\s+app\b"],
            "action": "open",
            "params": {"app": "youtube"},
            "description": "Open YouTube",
        },
        {
            "patterns": [r"\bopen\s*settings?\b"],
            "action": "open",
            "params": {"app": "settings"},
            "description": "Open Settings",
        },
        {
            "patterns": [r"\bopen\s*chrome\b", r"\blaunch\s*chrome\b", r"\bopen\s*browser\b"],
            "action": "open",
            "params": {"app": "chrome"},
            "description": "Open Chrome",
        },
        {
            "patterns": [r"\bopen\s*camera\b", r"\btake\s*(a\s*)?photo\b"],
            "action": "open",
            "params": {"app": "camera"},
            "description": "Open Camera",
        },
        {
            "patterns": [r"\bopen\s*whatsapp\b"],
            "action": "open",
            "params": {"app": "whatsapp"},
            "description": "Open WhatsApp",
        },
        {
            "patterns": [r"\bopen\s*instagram\b"],
            "action": "open",
            "params": {"app": "instagram"},
            "description": "Open Instagram",
        },
        {
            "patterns": [r"\bopen\s*telegram\b"],
            "action": "open",
            "params": {"app": "telegram"},
            "description": "Open Telegram",
        },
        {
            "patterns": [r"\bopen\s*(google\s*)?maps?\b"],
            "action": "open",
            "params": {"app": "maps"},
            "description": "Open Google Maps",
        },
        {
            "patterns": [r"\bopen\s*(phone|dialer|call)\b"],
            "action": "open",
            "params": {"app": "phone"},
            "description": "Open Phone/Dialer",
        },
        {
            "patterns": [r"\bopen\s*(messages?|sms|chat)\b"],
            "action": "open",
            "params": {"app": "messages"},
            "description": "Open Messages",
        },
        {
            "patterns": [r"\bopen\s*(gallery|photos?)\b"],
            "action": "open",
            "params": {"app": "gallery"},
            "description": "Open Gallery",
        },
        {
            "patterns": [r"\bopen\s*(calculator|calc)\b"],
            "action": "open",
            "params": {"app": "calculator"},
            "description": "Open Calculator",
        },
        {
            "patterns": [r"\bopen\s*(clock|alarm|timer)\b"],
            "action": "open",
            "params": {"app": "clock"},
            "description": "Open Clock",
        },
        {
            "patterns": [r"\bopen\s*(calendar|schedule)\b"],
            "action": "open",
            "params": {"app": "calendar"},
            "description": "Open Calendar",
        },
        {
            "patterns": [r"\bopen\s*(play\s*store|app\s*store)\b"],
            "action": "open",
            "params": {"app": "appstore"},
            "description": "Open App Store",
        },
        {
            "patterns": [r"\bopen\s*spotify\b"],
            "action": "open",
            "params": {"app": "spotify"},
            "description": "Open Spotify",
        },
        {
            "patterns": [r"\bopen\s*netflix\b"],
            "action": "open",
            "params": {"app": "netflix"},
            "description": "Open Netflix",
        },
        {
            "patterns": [r"\bopen\s*gmail\b"],
            "action": "open",
            "params": {"app": "gmail"},
            "description": "Open Gmail",
        },
        {
            "patterns": [r"\bopen\s*notes?\b"],
            "action": "open",
            "params": {"app": "notes"},
            "description": "Open Notes",
        },
        {
            "patterns": [r"\bopen\s*weather\b"],
            "action": "open",
            "params": {"app": "weather"},
            "description": "Open Weather",
        },
        {
            "patterns": [r"\bopen\s*files?\b"],
            "action": "open",
            "params": {"app": "files"},
            "description": "Open File Manager",
        },

        # Generic open: "open <anything>"
        {
            "patterns": [r"\bopen\s+([\w\s]+?)(?:\s+and|\s+then|$)"],
            "action": "open",
            "params": {"app": "__CAPTURE__"},
            "description": "Open app",
            "capture_group": 1,
        },

        # Typing
        {
            "patterns": [r"\btype\s+(?:'([^']+)'|\"([^\"]+)\"|(.+))"],
            "action": "type",
            "params": {"text": "__CAPTURE__"},
            "description": "Type text",
            "capture_group": "coalesce",
        },
        {
            "patterns": [r"\binput\s+(?:'([^']+)'|\"([^\"]+)\"|(.+))"],
            "action": "type",
            "params": {"text": "__CAPTURE__"},
            "description": "Input text",
            "capture_group": "coalesce",
        },

        # Tap
        {
            "patterns": [r"\btap\s*(?:at\s*)?(\d+)\s*[, ]\s*(\d+)"],
            "action": "tap",
            "params": {"x": "__INT_1__", "y": "__INT_2__"},
            "description": "Tap coordinates",
        },

        # Swipe
        {
            "patterns": [r"\bswipe\s*(?:from\s*)?(\d+)\s*[, ]\s*(\d+)\s*(?:to\s*)?(\d+)\s*[, ]\s*(\d+)"],
            "action": "swipe",
            "params": {"x1": "__INT_1__", "y1": "__INT_2__", "x2": "__INT_3__", "y2": "__INT_4__"},
            "description": "Swipe gesture",
        },

        # Scroll
        {
            "patterns": [r"\bscroll\s*(down|up|left|right)\b"],
            "action": "scroll",
            "params": {"direction": "__CAPTURE__"},
            "description": "Scroll screen",
            "capture_group": 1,
        },

        # Volume
        {
            "patterns": [r"\bvolume\s*up\b", r"\bincrease\s*volume\b"],
            "action": "key",
            "params": {"key": "volume_up"},
            "description": "Volume up",
        },
        {
            "patterns": [r"\bvolume\s*down\b", r"\bdecrease\s*volume\b"],
            "action": "key",
            "params": {"key": "volume_down"},
            "description": "Volume down",
        },

        # Search patterns: "search <query> on youtube"
        {
            "patterns": [r"\bsearch\s+(.+?)\s+on\s+youtube\b"],
            "action": "multi",
            "params": {
                "steps": [
                    {"action": "open", "params": {"app": "youtube"}},
                    {"action": "wait", "params": {"seconds": 2}},
                    {"action": "tap", "params": {"x": 540, "y": 120}},  # Search icon area
                    {"action": "wait", "params": {"seconds": 0.5}},
                    {"action": "type", "params": {"text": "__CAPTURE__"}},
                    {"action": "key", "params": {"key": "enter"}},
                ]
            },
            "description": "Search on YouTube",
            "capture_group": 1,
        },

        # Screenshot
        {
            "patterns": [r"\btake\s*(a\s*)?screenshot\b", r"\bcapture\s*screen\b"],
            "action": "screenshot",
            "params": {},
            "description": "Take screenshot",
        },

        # Close app
        {
            "patterns": [r"\bclose\s+(?:the\s+)?(?:app\s+)?([\w\s]+?)(?:\s+and|\s+then|$)"],
            "action": "close",
            "params": {"app": "__CAPTURE__"},
            "description": "Close app",
            "capture_group": 1,
        },
    ]

    # Scroll direction → swipe params
    SCROLL_MAP = {
        "down": {"x1": 540, "y1": 1500, "x2": 540, "y2": 500, "duration": 300},
        "up": {"x1": 540, "y1": 500, "x2": 540, "y2": 1500, "duration": 300},
        "left": {"x1": 900, "y1": 1000, "x2": 200, "y2": 1000, "duration": 300},
        "right": {"x1": 200, "y1": 1000, "x2": 900, "y2": 1000, "duration": 300},
    }

    def parse(self, command: str) -> List[AgentAction]:
        """Parse natural language command into agent actions."""
        command = command.strip().lower()
        actions = []

        for intent in self.INTENT_PATTERNS:
            for pattern in intent["patterns"]:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    action = self._build_action(intent, match, command)
                    if action:
                        actions.append(action)
                    break  # First match per intent wins
            if actions:
                break  # Stop at first intent match

        # If no patterns matched, try fuzzy matching
        if not actions:
            actions = self._fuzzy_parse(command)

        return actions

    def _build_action(self, intent: Dict, match: re.Match, command: str) -> Optional[AgentAction]:
        """Build an AgentAction from matched intent."""
        action_type = intent["action"]
        params = dict(intent["params"])
        description = intent.get("description", "")
        capture_group = intent.get("capture_group")

        # Handle capture groups
        if capture_group and capture_group == "coalesce":
            # Get first non-None group
            captured = next((g for g in match.groups() if g), None)
            if captured:
                captured = captured.strip()
        elif capture_group:
            captured = match.group(capture_group)
        else:
            captured = None

        # Replace __CAPTURE__ in params
        for key, value in params.items():
            if isinstance(value, str) and value == "__CAPTURE__":
                if captured:
                    params[key] = captured
                else:
                    return None
            elif isinstance(value, dict):
                for k2, v2 in value.items():
                    if isinstance(v2, str) and v2 == "__CAPTURE__":
                        if captured:
                            params[k2] = captured

        # Replace __INT_N__ in params (format: __INT_1__, __INT_2__, etc.)
        import re as _re
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("__INT_"):
                int_match = _re.match(r'__INT_(\d+)__', value)
                if int_match:
                    idx = int(int_match.group(1))
                    try:
                        params[key] = int(match.group(idx))
                    except (IndexError, ValueError):
                        return None

        # Handle multi-step actions
        if action_type == "multi":
            steps = params.get("steps", [])
            agent_actions = []
            for step in steps:
                step_action = step.get("action", "")
                step_params = dict(step.get("params", {}))

                # Replace captures in nested steps
                for k, v in step_params.items():
                    if isinstance(v, str) and v == "__CAPTURE__":
                        if captured:
                            step_params[k] = captured

                agent_actions.append(
                    AgentAction(
                        action_type=step_action,
                        params=step_params,
                        description=f"Multi-step: {step_action}",
                    )
                )
            return agent_actions  # Returns a list!

        # Handle scroll → swipe conversion
        if action_type == "scroll":
            direction = params.get("direction", "down")
            scroll_params = self.SCROLL_MAP.get(direction, self.SCROLL_MAP["down"])
            return AgentAction(
                action_type="swipe",
                params=scroll_params,
                description=description,
            )

        return AgentAction(
            action_type=action_type,
            params=params,
            description=description,
        )

    def _fuzzy_parse(self, command: str) -> List[AgentAction]:
        """Fuzzy matching for unrecognized commands."""
        if not command or not command.strip():
            return []
        # Check if it looks like an app name
        words = command.split()
        if len(words) <= 3:
            # Try as app open
            return [AgentAction(
                action_type="open",
                params={"app": command},
                description=f"Try opening '{command}'",
                confidence=0.5,
            )]
        return []


class HyperPilotAgent:
    """AI Agent that parses commands and executes on device."""

    def __init__(self, adb: ADBController, mode: AgentMode = AgentMode.LOCAL, openai_key: Optional[str] = None):
        self.adb = adb
        self.mode = mode
        self.parser = CommandParser()
        self.openai_key = openai_key
        self.history: List[AgentResponse] = []

    def process_command(self, command: str) -> AgentResponse:
        """Main entry: natural language → device action → response."""
        start = time.time()
        response = AgentResponse(command=command)

        try:
            # Step 1: Parse command
            actions = self.parser.parse(command)

            if not actions:
                response.final_result = f"🤔 I don't understand: '{command}'. Try: 'open youtube', 'go home', 'type hello'"
                response.success = False
                response.reasoning = "No matching intent found"
                return response

            # Flatten multi-step
            flat_actions = []
            for a in actions:
                if isinstance(a, list):
                    flat_actions.extend(a)
                else:
                    flat_actions.append(a)

            response.parsed_actions = flat_actions

            # Step 2: Execute actions
            steps = []
            all_success = True

            for action in flat_actions:
                step = AgentStep(
                    thought=f"Executing: {action.description or action.action_type}",
                    action=action,
                    timestamp=time.time(),
                )

                result = self._execute_action(action)
                step.result = result

                if not result.success:
                    all_success = False

                steps.append(step)

            response.steps = steps
            response.success = all_success

            # Step 3: Build result message
            if all_success:
                descriptions = [a.description for a in flat_actions if a.description]
                response.final_result = f"✅ Done! {' → '.join(descriptions) if descriptions else 'Actions executed.'}"
            else:
                failed = [s for s in steps if s.result and not s.result.success]
                if failed:
                    errors = [s.result.error for s in failed]
                    response.final_result = f"⚠️ Partial success. Errors: {'; '.join(errors)}"
                else:
                    response.final_result = "⚠️ Some actions may have failed."

            response.reasoning = self._build_reasoning(steps)

        except Exception as e:
            response.final_result = f"❌ Agent error: {str(e)}"
            response.success = False

        response.execution_time_ms = (time.time() - start) * 1000
        self.history.append(response)
        return response

    def _execute_action(self, action: AgentAction) -> ADBResult:
        """Route a single action to the appropriate ADB method."""
        t = action.action_type
        p = action.params

        if t == "key":
            return self.adb.press_key(p.get("key", "home"))
        elif t == "tap":
            return self.adb.tap(p.get("x", 0), p.get("y", 0))
        elif t == "swipe":
            return self.adb.swipe(
                p.get("x1", 0), p.get("y1", 0),
                p.get("x2", 0), p.get("y2", 0),
                p.get("duration", 300),
            )
        elif t == "type":
            # Wake screen first
            self.adb.wake_screen()
            time.sleep(0.3)
            return self.adb.type_text(p.get("text", ""))
        elif t == "open":
            self.adb.wake_screen()
            time.sleep(0.5)
            return self.adb.open_app(p.get("app", ""))
        elif t == "close":
            return self.adb.close_app(p.get("app", ""))
        elif t == "screenshot":
            return self.adb.screenshot()
        elif t == "shell":
            return self.adb.shell(p.get("cmd", ""))
        elif t == "wait":
            time.sleep(p.get("seconds", 1))
            return ADBResult(success=True, output="Waited")
        else:
            return ADBResult(success=False, error=f"Unknown action type: {t}")

    def _build_reasoning(self, steps: List[AgentStep]) -> str:
        """Build a human-readable reasoning log."""
        lines = ["🧠 **Agent Reasoning:**\n"]
        for i, step in enumerate(steps, 1):
            status = "✅" if step.result and step.result.success else "❌"
            cmd = step.result.command if step.result else "?"
            ms = f" ({step.result.duration_ms:.0f}ms)" if step.result else ""
            lines.append(f"{i}. {status} {step.thought}{ms}")
            lines.append(f"   `{cmd}`")
        return "\n".join(lines)

    def get_quick_actions(self) -> List[Dict[str, str]]:
        """Return quick action buttons for the UI."""
        return [
            {"label": "🏠 Home", "command": "go home"},
            {"label": "◀️ Back", "command": "go back"},
            {"label": "📱 Recent", "command": "recent apps"},
            {"label": "📸 Screenshot", "command": "take screenshot"},
            {"label": "🔧 Settings", "command": "open settings"},
            {"label": "📺 YouTube", "command": "open youtube"},
            {"label": "🌐 Chrome", "command": "open chrome"},
            {"label": "📷 Camera", "command": "open camera"},
            {"label": "💬 WhatsApp", "command": "open whatsapp"},
            {"label": "🎵 Spotify", "command": "open spotify"},
            {"label": "⬆️ Vol Up", "command": "volume up"},
            {"label": "⬇️ Vol Down", "command": "volume down"},
            {"label": "🔄 Scroll Down", "command": "scroll down"},
            {"label": "⬆️ Scroll Up", "command": "scroll up"},
        ]
