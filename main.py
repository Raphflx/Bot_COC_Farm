import json
import logging
import signal
import sys
import time
from pathlib import Path

from src.adb.controller import ADBController, ADBError
from src.bot.farming import FarmingBot
from src.bot.state import State, StateMachine
from src.notifications.notifier import Notifier
from src.vision.detector import Detector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

_RUNNING = True


def _handle_sigint(sig: int, frame: object) -> None:
    global _RUNNING
    logger.info("Interrupt received — stopping after current cycle")
    _RUNNING = False


def load_config(path: str = "config.json") -> dict:
    """Load bot configuration from a JSON file.

    Args:
        path: Path to the config file.

    Returns:
        Parsed configuration dictionary.
    """
    config_path = Path(path)
    if not config_path.exists():
        logger.warning("config.json not found — using config.example.json")
        config_path = Path("config.example.json")
    with config_path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    """Entry point: connect to BlueStacks and run the main bot loop."""
    signal.signal(signal.SIGINT, _handle_sigint)

    config = load_config()
    adb_cfg = config.get("adb", {})
    bot_cfg = config.get("bot", {})
    vis_cfg = config.get("vision", {})
    notif_cfg = config.get("notifications", {})

    Path("logs").mkdir(exist_ok=True)

    controller = ADBController(
        host=adb_cfg.get("host", "127.0.0.1"),
        port=adb_cfg.get("port", 5555),
        adb_path=adb_cfg.get("adb_path", "adb"),
        timeout=adb_cfg.get("timeout", 30),
    )
    detector = Detector(
        templates_dir=vis_cfg.get("templates_path", "src/vision/templates"),
        confidence=vis_cfg.get("confidence_threshold", 0.85),
    )
    notifier = Notifier(
        discord_webhook_url=notif_cfg.get("discord_webhook_url", ""),
        telegram_bot_token=notif_cfg.get("telegram_bot_token", ""),
        telegram_chat_id=notif_cfg.get("telegram_chat_id", ""),
    )
    farming_bot = FarmingBot(controller, detector)
    sm = StateMachine()

    max_hours = bot_cfg.get("max_run_hours", 6)
    start_time = time.time()

    logger.info("Starting bot (max runtime: %dh)", max_hours)
    sm.transition(State.CONNECTING)

    try:
        if not controller.connect():
            raise ADBError("Could not connect to BlueStacks — run `adb connect 127.0.0.1:5555`")
    except ADBError as exc:
        logger.error("ADB error during startup: %s", exc)
        sm.transition(State.ERROR)
        sys.exit(1)

    sm.transition(State.HOME_VILLAGE)
    notifier.send("Bot started")

    while _RUNNING:
        elapsed_hours = (time.time() - start_time) / 3600
        if elapsed_hours >= max_hours:
            logger.info("Max runtime reached (%.1fh) — stopping", elapsed_hours)
            break

        sm.transition(State.FARMING)
        try:
            collected = farming_bot.collect_all()
            if collected:
                notifier.send(f"Farming cycle: tapped {collected} buildings")
        except ADBError as exc:
            logger.error("ADB error during farming: %s", exc)
            sm.transition(State.ERROR)
            break

        sm.transition(State.HOME_VILLAGE)
        # Wait ~5 minutes before the next collection cycle
        cycle_wait = 300
        logger.info("Cycle complete — next cycle in %ds", cycle_wait)
        for _ in range(cycle_wait):
            if not _RUNNING:
                break
            time.sleep(1)

    sm.transition(State.STOPPING)
    controller.disconnect()
    notifier.send("Bot stopped")
    logger.info("Bot stopped cleanly")


if __name__ == "__main__":
    main()
