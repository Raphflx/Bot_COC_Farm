import logging
import random
import subprocess
import time

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ADBError(Exception):
    """Raised when an ADB command fails or the device is unreachable."""


class ADBController:
    """Controls a BlueStacks instance via ADB.

    Example:
        controller = ADBController()
        controller.connect()
        img = controller.screenshot()
        controller.tap(640, 360)
        controller.swipe(100, 500, 900, 500)
    """

    DEFAULT_HOST: str = "127.0.0.1"
    DEFAULT_PORT: int = 5555

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        adb_path: str = "adb",
        timeout: int = 30,
    ) -> None:
        """Initialize the controller.

        Args:
            host: ADB host address (BlueStacks default: 127.0.0.1).
            port: ADB port (BlueStacks default: 5555).
            adb_path: Path to the adb binary (must be in PATH or absolute).
            timeout: Subprocess timeout in seconds.
        """
        self.host = host
        self.port = port
        self.serial = f"{host}:{port}"
        self._adb = adb_path
        self._timeout = timeout
        self._connected = False

    # -------------------------------------------------------------------------
    # Connection
    # -------------------------------------------------------------------------

    def connect(self) -> bool:
        """Connect to the BlueStacks instance.

        Returns:
            True if the connection succeeded, False otherwise.
        """
        logger.info("Connecting to %s", self.serial)
        output = self._run(["connect", self.serial])
        if "connected" in output.lower():
            self._connected = True
            logger.info("ADB connected to %s", self.serial)
            return True
        logger.error("Connection failed: %s", output)
        return False

    def disconnect(self) -> None:
        """Disconnect from the device."""
        self._run(["disconnect", self.serial])
        self._connected = False
        logger.info("ADB disconnected from %s", self.serial)

    def is_connected(self) -> bool:
        """Check whether the device is currently listed by adb devices.

        Returns:
            True if the serial appears in the device list.
        """
        output = self._run(["devices"])
        return self.serial in output

    # -------------------------------------------------------------------------
    # Screen capture
    # -------------------------------------------------------------------------

    def screenshot(self) -> np.ndarray:
        """Capture the device screen and return it as a BGR numpy array.

        Returns:
            OpenCV-compatible BGR image of shape (H, W, 3).

        Raises:
            ADBError: if the capture returns empty data or cannot be decoded.
        """
        self._assert_connected()
        logger.debug("Capturing screenshot from %s", self.serial)
        raw = self._run_bytes(["-s", self.serial, "exec-out", "screencap", "-p"])
        if not raw:
            raise ADBError("Screenshot returned empty data — is the device awake?")
        arr = np.frombuffer(raw, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ADBError("cv2.imdecode failed — screencap output may be corrupted")
        logger.debug("Screenshot captured: %dx%d px", img.shape[1], img.shape[0])
        return img

    # -------------------------------------------------------------------------
    # Input simulation
    # -------------------------------------------------------------------------

    def tap(
        self,
        x: int,
        y: int,
        delay_min: float = 0.5,
        delay_max: float = 1.5,
    ) -> None:
        """Tap at screen coordinates with a random post-action delay.

        Args:
            x: Horizontal coordinate in pixels (1280x720 reference resolution).
            y: Vertical coordinate in pixels (1280x720 reference resolution).
            delay_min: Minimum wait time in seconds after the tap.
            delay_max: Maximum wait time in seconds after the tap.
        """
        self._assert_connected()
        logger.info("Tap  (%d, %d)", x, y)
        self._shell(["input", "tap", str(x), str(y)])
        self._random_sleep(delay_min, delay_max)

    def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration_ms: int = 300,
        delay_min: float = 0.5,
        delay_max: float = 1.5,
    ) -> None:
        """Swipe from one point to another.

        Args:
            x1: Start horizontal coordinate.
            y1: Start vertical coordinate.
            x2: End horizontal coordinate.
            y2: End vertical coordinate.
            duration_ms: Duration of the swipe gesture in milliseconds.
            delay_min: Minimum wait time in seconds after the swipe.
            delay_max: Maximum wait time in seconds after the swipe.
        """
        self._assert_connected()
        logger.info("Swipe (%d,%d) -> (%d,%d)  %dms", x1, y1, x2, y2, duration_ms)
        self._shell(
            ["input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)]
        )
        self._random_sleep(delay_min, delay_max)

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _assert_connected(self) -> None:
        if not self._connected:
            raise ADBError("Device not connected — call connect() first")

    def _random_sleep(self, low: float, high: float) -> None:
        delay = random.uniform(low, high)
        logger.debug("Delay %.2fs", delay)
        time.sleep(delay)

    def _run(self, args: list[str]) -> str:
        """Execute an adb command and return stdout as a string.

        Args:
            args: Arguments passed to the adb binary (without 'adb' itself).

        Returns:
            Decoded stdout output, stripped of trailing whitespace.

        Raises:
            ADBError: if the binary is not found or the command times out.
        """
        cmd = [self._adb] + args
        logger.debug("$ %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
            if result.returncode != 0 and result.stderr:
                logger.warning("adb stderr: %s", result.stderr.strip())
            return result.stdout.strip()
        except FileNotFoundError:
            raise ADBError(
                f"adb binary not found at '{self._adb}' — add ADB to PATH"
            ) from None
        except subprocess.TimeoutExpired:
            raise ADBError(f"ADB command timed out after {self._timeout}s") from None

    def _run_bytes(self, args: list[str]) -> bytes:
        """Execute an adb command and return raw stdout bytes.

        Args:
            args: Arguments passed to the adb binary.

        Returns:
            Raw bytes from stdout (used for binary output like screencap).

        Raises:
            ADBError: if the binary is not found or the command times out.
        """
        cmd = [self._adb] + args
        logger.debug("$ %s  (binary)", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self._timeout,
            )
            return result.stdout
        except FileNotFoundError:
            raise ADBError(
                f"adb binary not found at '{self._adb}' — add ADB to PATH"
            ) from None
        except subprocess.TimeoutExpired:
            raise ADBError(f"ADB command timed out after {self._timeout}s") from None

    def _shell(self, args: list[str]) -> str:
        """Run a shell command on the connected device.

        Args:
            args: Shell command split as a list (e.g. ['input', 'tap', '100', '200']).

        Returns:
            Decoded stdout output.
        """
        return self._run(["-s", self.serial, "shell"] + args)
