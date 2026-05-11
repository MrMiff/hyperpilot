"""Tests for HyperPilot Agent command parser."""

import pytest
from agent import CommandParser, HyperPilotAgent, AgentMode
from adb_controller import ADBController


@pytest.fixture
def parser():
    return CommandParser()


@pytest.fixture
def agent():
    adb = ADBController()
    return HyperPilotAgent(adb, mode=AgentMode.LOCAL)


class TestNavigationIntents:
    """Test basic navigation commands."""

    def test_go_home(self, parser):
        actions = parser.parse("go home")
        assert len(actions) == 1
        assert actions[0].action_type == "key"
        assert actions[0].params["key"] == "home"

    def test_go_back(self, parser):
        actions = parser.parse("go back")
        assert len(actions) == 1
        assert actions[0].action_type == "key"
        assert actions[0].params["key"] == "back"

    def test_recent_apps(self, parser):
        actions = parser.parse("recent apps")
        assert len(actions) == 1
        assert actions[0].action_type == "key"
        assert actions[0].params["key"] == "recent"

    def test_volume_up(self, parser):
        actions = parser.parse("volume up")
        assert len(actions) == 1
        assert actions[0].action_type == "key"
        assert actions[0].params["key"] == "volume_up"

    def test_volume_down(self, parser):
        actions = parser.parse("volume down")
        assert len(actions) == 1
        assert actions[0].action_type == "key"
        assert actions[0].params["key"] == "volume_down"


class TestAppLaunch:
    """Test app launching commands."""

    @pytest.mark.parametrize("command,expected_app", [
        ("open youtube", "youtube"),
        ("open settings", "settings"),
        ("open chrome", "chrome"),
        ("open camera", "camera"),
        ("open whatsapp", "whatsapp"),
        ("open instagram", "instagram"),
        ("open telegram", "telegram"),
        ("open spotify", "spotify"),
        ("open netflix", "netflix"),
        ("open gmail", "gmail"),
        ("open maps", "maps"),
        ("open calculator", "calculator"),
        ("open notes", "notes"),
        ("open weather", "weather"),
        ("open files", "files"),
    ])
    def test_open_app(self, parser, command, expected_app):
        actions = parser.parse(command)
        flat = []
        for a in actions:
            if isinstance(a, list):
                flat.extend(a)
            else:
                flat.append(a)
        assert len(flat) >= 1
        assert flat[0].action_type == "open"
        assert flat[0].params["app"] == expected_app

    def test_launch_youtube(self, parser):
        actions = parser.parse("launch youtube")
        assert len(actions) == 1
        assert actions[0].action_type == "open"
        assert actions[0].params["app"] == "youtube"


class TestTextInput:
    """Test text input commands."""

    def test_type_text(self, parser):
        actions = parser.parse("type hello world")
        assert len(actions) == 1
        assert actions[0].action_type == "type"
        assert actions[0].params["text"] == "hello world"

    def test_type_quoted_text(self, parser):
        actions = parser.parse("type 'search query'")
        assert len(actions) == 1
        assert actions[0].action_type == "type"
        assert "search query" in actions[0].params["text"]

    def test_input_text(self, parser):
        actions = parser.parse("input hello")
        assert len(actions) == 1
        assert actions[0].action_type == "type"


class TestScreenControl:
    """Test screen control commands."""

    def test_scroll_down(self, parser):
        actions = parser.parse("scroll down")
        assert len(actions) == 1
        assert actions[0].action_type == "swipe"
        # Swipe up = scroll down
        assert actions[0].params["y1"] > actions[0].params["y2"]

    def test_scroll_up(self, parser):
        actions = parser.parse("scroll up")
        assert len(actions) == 1
        assert actions[0].action_type == "swipe"
        assert actions[0].params["y1"] < actions[0].params["y2"]

    def test_tap_coordinates(self, parser):
        actions = parser.parse("tap 500 1000")
        assert len(actions) == 1
        assert actions[0].action_type == "tap"
        assert actions[0].params["x"] == 500
        assert actions[0].params["y"] == 1000

    def test_swipe(self, parser):
        actions = parser.parse("swipe 100 500 100 1500")
        assert len(actions) == 1
        assert actions[0].action_type == "swipe"
        assert actions[0].params["x1"] == 100
        assert actions[0].params["y1"] == 500
        assert actions[0].params["x2"] == 100
        assert actions[0].params["y2"] == 1500


class TestMultiStep:
    """Test multi-step workflow commands."""

    def test_search_youtube(self, parser):
        actions = parser.parse("search lofi music on youtube")
        flat = []
        for a in actions:
            if isinstance(a, list):
                flat.extend(a)
            else:
                flat.append(a)

        assert len(flat) >= 4  # open, wait, tap, type, enter
        assert flat[0].action_type == "open"
        assert flat[0].params["app"] == "youtube"

        # Find the type action
        type_actions = [a for a in flat if a.action_type == "type"]
        assert len(type_actions) == 1
        assert type_actions[0].params["text"] == "lofi music"

    def test_search_youtube_different_query(self, parser):
        actions = parser.parse("search chill vibes on youtube")
        flat = []
        for a in actions:
            if isinstance(a, list):
                flat.extend(a)
            else:
                flat.append(a)

        type_actions = [a for a in flat if a.action_type == "type"]
        assert len(type_actions) == 1
        assert type_actions[0].params["text"] == "chill vibes"


class TestCloseApp:
    """Test close app commands."""

    def test_close_app(self, parser):
        actions = parser.parse("close chrome")
        assert len(actions) == 1
        assert actions[0].action_type == "close"
        assert actions[0].params["app"] == "chrome"


class TestScreenshot:
    """Test screenshot command."""

    def test_screenshot(self, parser):
        actions = parser.parse("take screenshot")
        assert len(actions) == 1
        assert actions[0].action_type == "screenshot"


class TestEdgeCases:
    """Test edge cases and fuzzy matching."""

    def test_empty_command(self, parser):
        actions = parser.parse("")
        assert len(actions) == 0

    def test_unknown_command_fuzzy(self, parser):
        """Unknown commands should try to open as app."""
        actions = parser.parse("myapp")
        # Should fall through to fuzzy parser
        assert len(actions) >= 1


class TestAgentQuickActions:
    """Test agent quick action buttons."""

    def test_quick_actions_count(self, agent):
        qa = agent.get_quick_actions()
        assert len(qa) >= 10

    def test_quick_actions_have_required_keys(self, agent):
        qa = agent.get_quick_actions()
        for action in qa:
            assert "label" in action
            assert "command" in action
