import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.vision.detector import Detector


@pytest.fixture
def templates_dir(tmp_path: Path) -> Path:
    """Create a temporary templates directory with a dummy template."""
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    # Create a 50x50 white square template
    tpl = np.full((50, 50, 3), 255, dtype=np.uint8)
    cv2.imwrite(str(tpl_dir / "white_square.png"), tpl)
    return tpl_dir


@pytest.fixture
def detector(templates_dir: Path) -> Detector:
    return Detector(templates_dir=str(templates_dir), confidence=0.85)


class TestFind:
    def test_find_existing_template(self, detector: Detector) -> None:
        # Screenshot: dark background with white square at (100, 100)
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        screenshot[100:150, 100:150] = 255
        result = detector.find(screenshot, "white_square")
        assert result is not None
        x, y = result
        assert abs(x - 125) < 5
        assert abs(y - 125) < 5

    def test_find_returns_none_when_not_present(self, detector: Detector) -> None:
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        result = detector.find(screenshot, "white_square")
        assert result is None

    def test_find_raises_on_missing_template(self, detector: Detector) -> None:
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        with pytest.raises(FileNotFoundError):
            detector.find(screenshot, "nonexistent_template")

    def test_find_returns_none_on_empty_screenshot(self, detector: Detector) -> None:
        result = detector.find(np.array([]), "white_square")
        assert result is None


class TestFindAll:
    def test_find_all_returns_multiple_matches(self, detector: Detector) -> None:
        screenshot = np.zeros((720, 1280, 3), dtype=np.uint8)
        screenshot[100:150, 100:150] = 255
        screenshot[300:350, 600:650] = 255
        results = detector.find_all(screenshot, "white_square")
        assert len(results) >= 2
