import logging
from typing import Optional

from src.adb.controller import ADBController
from src.vision.detector import Detector

logger = logging.getLogger(__name__)


class AttackBot:
    """Handles base searching and troop deployment for automatic attacks.

    Example:
        bot = AttackBot(controller, detector)
        found = bot.find_target()
        if found:
            bot.deploy_troops()
    """

    def __init__(self, controller: ADBController, detector: Detector) -> None:
        """Initialize the attack bot.

        Args:
            controller: Connected ADB controller.
            detector: Vision detector with templates loaded.
        """
        self.controller = controller
        self.detector = detector

    def find_target(self, max_skips: int = 20) -> bool:
        """Search for a suitable base to attack.

        Presses "Next" up to max_skips times looking for a base that meets
        the minimum resource thresholds defined in config.

        Args:
            max_skips: Maximum number of bases to skip before giving up.

        Returns:
            True if a suitable base was found, False otherwise.
        """
        logger.info("Searching for target (max %d skips)", max_skips)
        # TODO: implement resource-threshold evaluation
        return False

    def deploy_troops(self, positions: Optional[list[tuple[int, int]]] = None) -> None:
        """Deploy troops along the bottom edge of the map.

        Args:
            positions: Optional explicit list of (x, y) deployment points.
                       Defaults to a spread across the bottom border.
        """
        # Default deployment: spread across the bottom of the 1280x720 screen
        if positions is None:
            positions = [(x, 650) for x in range(200, 1100, 100)]
        logger.info("Deploying troops at %d positions", len(positions))
        for x, y in positions:
            self.controller.tap(x, y)
