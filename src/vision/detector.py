import logging
import os
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class Detector:
    """Template-matching based detector using OpenCV.

    Example:
        detector = Detector("src/vision/templates")
        match = detector.find(screenshot, "gold_collector")
        if match:
            x, y = match
    """

    def __init__(
        self,
        templates_dir: str = "src/vision/templates",
        confidence: float = 0.85,
    ) -> None:
        """Initialize the detector.

        Args:
            templates_dir: Path to the directory containing reference PNG templates.
            confidence: Minimum match score in [0, 1] to accept a detection.
        """
        self.templates_dir = Path(templates_dir)
        self.confidence = confidence
        self._cache: dict[str, np.ndarray] = {}

    def find(
        self,
        screenshot: np.ndarray,
        template_name: str,
        confidence: Optional[float] = None,
    ) -> Optional[tuple[int, int]]:
        """Locate a template in a screenshot and return its centre coordinates.

        Args:
            screenshot: BGR image captured from the device.
            template_name: Filename stem of the template (without .png extension).
            confidence: Override the instance-level confidence threshold.

        Returns:
            (x, y) centre of the best match, or None if below threshold.

        Raises:
            FileNotFoundError: if the template image does not exist.
        """
        if screenshot is None or screenshot.size == 0:
            logger.error("screenshot is empty — skipping detection for '%s'", template_name)
            return None

        threshold = confidence if confidence is not None else self.confidence
        template = self._load_template(template_name)
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        logger.debug("Template '%s' best score: %.3f (threshold %.2f)", template_name, max_val, threshold)

        if max_val < threshold:
            return None

        th, tw = template.shape[:2]
        cx = max_loc[0] + tw // 2
        cy = max_loc[1] + th // 2
        logger.info("Found '%s' at (%d, %d) score=%.3f", template_name, cx, cy, max_val)
        return cx, cy

    def find_all(
        self,
        screenshot: np.ndarray,
        template_name: str,
        confidence: Optional[float] = None,
    ) -> list[tuple[int, int]]:
        """Locate all non-overlapping occurrences of a template.

        Args:
            screenshot: BGR image from the device.
            template_name: Filename stem of the template.
            confidence: Override the instance-level confidence threshold.

        Returns:
            List of (x, y) centre coordinates for every match found.
        """
        threshold = confidence if confidence is not None else self.confidence
        template = self._load_template(template_name)
        th, tw = template.shape[:2]

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches: list[tuple[int, int]] = []

        for pt in zip(*locations[::-1]):
            cx = pt[0] + tw // 2
            cy = pt[1] + th // 2
            matches.append((cx, cy))

        logger.info("Found %d instance(s) of '%s'", len(matches), template_name)
        return matches

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _load_template(self, name: str) -> np.ndarray:
        """Load a template from disk (cached after first load).

        Args:
            name: Filename stem (without .png extension).

        Returns:
            BGR numpy array for the template image.

        Raises:
            FileNotFoundError: if the PNG file does not exist.
        """
        if name in self._cache:
            return self._cache[name]

        path = self.templates_dir / f"{name}.png"
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")

        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to load template image: {path}")

        self._cache[name] = img
        logger.debug("Template '%s' loaded (%dx%d)", name, img.shape[1], img.shape[0])
        return img
