import subprocess
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.adb.controller import ADBController, ADBError


@pytest.fixture
def controller() -> ADBController:
    return ADBController(host="127.0.0.1", port=5555)


class TestConnect:
    def test_connect_success(self, controller: ADBController) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="connected to 127.0.0.1:5555", returncode=0, stderr="")
            assert controller.connect() is True
            assert controller._connected is True

    def test_connect_failure(self, controller: ADBController) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="failed to connect", returncode=1, stderr="")
            assert controller.connect() is False
            assert controller._connected is False

    def test_adb_not_found_raises(self, controller: ADBController) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(ADBError, match="not found"):
                controller.connect()


class TestScreenshot:
    def test_screenshot_returns_numpy_array(self, controller: ADBController) -> None:
        controller._connected = True
        # Create a minimal valid PNG in memory
        import cv2
        dummy_img = np.zeros((720, 1280, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".png", dummy_img)
        png_bytes = encoded.tobytes()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=png_bytes, returncode=0)
            result = controller.screenshot()

        assert isinstance(result, np.ndarray)
        assert result.shape == (720, 1280, 3)

    def test_screenshot_raises_when_not_connected(self, controller: ADBController) -> None:
        with pytest.raises(ADBError, match="not connected"):
            controller.screenshot()

    def test_screenshot_raises_on_empty_data(self, controller: ADBController) -> None:
        controller._connected = True
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=b"", returncode=0)
            with pytest.raises(ADBError, match="empty"):
                controller.screenshot()


class TestTap:
    def test_tap_calls_adb_shell(self, controller: ADBController) -> None:
        controller._connected = True
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0, stderr="")
            with patch("time.sleep"):
                controller.tap(100, 200, delay_min=0.1, delay_max=0.1)
        cmd = mock_run.call_args[0][0]
        assert "input" in cmd
        assert "tap" in cmd
        assert "100" in cmd
        assert "200" in cmd

    def test_tap_raises_when_not_connected(self, controller: ADBController) -> None:
        with pytest.raises(ADBError):
            controller.tap(0, 0)


class TestSwipe:
    def test_swipe_calls_adb_shell(self, controller: ADBController) -> None:
        controller._connected = True
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0, stderr="")
            with patch("time.sleep"):
                controller.swipe(0, 0, 500, 500, duration_ms=200)
        cmd = mock_run.call_args[0][0]
        assert "swipe" in cmd
        assert "200" in cmd
