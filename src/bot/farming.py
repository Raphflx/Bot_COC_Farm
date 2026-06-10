import logging

from src.adb.controller import ADBController
from src.vision.detector import Detector

logger = logging.getLogger(__name__)


class FarmingBot:
    """Automates resource collection from collectors and mines.

    Example:
        bot = FarmingBot(controller, detector)
        bot.collect_all()
    """

    # Template names expected in src/vision/templates/
    COLLECTOR_TEMPLATES: list[str] = [
        "gold_mine_full",
        "elixir_collector_full",
        "dark_elixir_drill_full",
    ]

    def __init__(self, controller: ADBController, detector: Detector) -> None:
        """Initialize the farming bot.

        Args:
            controller: Connected ADB controller.
            detector: Vision detector with templates loaded.
        """
        self.controller = controller
        self.detector = detector

    def collect_all(self) -> int:
        """Collect resources from every full collector/mine on screen.

        Returns:
            Number of collectors tapped.
        """
        screenshot = self.controller.screenshot()
        total = 0
        for template in self.COLLECTOR_TEMPLATES:
            try:
                locations = self.detector.find_all(screenshot, template)
            except FileNotFoundError:
                logger.warning("Template '%s' not found — skipping", template)
                continue
            for x, y in locations:
                logger.info("Collecting from %s at (%d, %d)", template, x, y)
                self.controller.tap(x, y)
                total += 1
        logger.info("Collected from %d buildings", total)
        return total
