import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class Notifier:
    """Sends notifications via Discord webhooks and/or Telegram bot API.

    Example:
        notifier = Notifier(discord_webhook_url="https://discord.com/api/webhooks/...")
        notifier.send("Farming cycle complete — +500k gold")
    """

    def __init__(
        self,
        discord_webhook_url: str = "",
        telegram_bot_token: str = "",
        telegram_chat_id: str = "",
        timeout: int = 10,
    ) -> None:
        """Initialize the notifier.

        Args:
            discord_webhook_url: Discord incoming webhook URL.
            telegram_bot_token: Telegram bot token from BotFather.
            telegram_chat_id: Target chat or channel ID.
            timeout: HTTP request timeout in seconds.
        """
        self._discord_url = discord_webhook_url
        self._tg_token = telegram_bot_token
        self._tg_chat = telegram_chat_id
        self._timeout = timeout

    def send(self, message: str) -> None:
        """Send a notification to all configured channels.

        Args:
            message: Plain-text message to deliver.
        """
        if self._discord_url:
            self._send_discord(message)
        if self._tg_token and self._tg_chat:
            self._send_telegram(message)

    def _send_discord(self, message: str) -> None:
        """Post a message to the Discord webhook.

        Args:
            message: Text to post.
        """
        try:
            response = requests.post(
                self._discord_url,
                json={"content": message},
                timeout=self._timeout,
            )
            response.raise_for_status()
            logger.info("Discord notification sent")
        except requests.RequestException as exc:
            logger.error("Discord notification failed: %s", exc)

    def _send_telegram(self, message: str) -> None:
        """Send a message via the Telegram Bot API.

        Args:
            message: Text to send.
        """
        url = f"https://api.telegram.org/bot{self._tg_token}/sendMessage"
        try:
            response = requests.post(
                url,
                json={"chat_id": self._tg_chat, "text": message},
                timeout=self._timeout,
            )
            response.raise_for_status()
            logger.info("Telegram notification sent")
        except requests.exceptions.HTTPError as exc:
            # Log only the HTTP status code — the URL contains the bot token
            logger.error("Telegram notification failed: HTTP %s", exc.response.status_code)
        except requests.RequestException as exc:
            logger.error("Telegram notification failed: %s", type(exc).__name__)
