# notifications.py
import os
import logging
import requests

class TelegramNotifier:
    """
    A class to handle sending alerts to Telegram.
    """

    def __init__(self):
        """
        Initializes the notifier, getting token and chat ID from environment variables.
        """
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.is_configured = self.token is not None and self.chat_id is not None

        if not self.is_configured:
            logging.warning("Telegram token or chat ID not set. Notifications are disabled.")

    def send_alert(self, message: str):
        """
        Sends an alert message to Telegram if configured.

        Args:
            message (str): The message to send.
        """
        if not self.is_configured:
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            logging.info("Telegram alert sent successfully.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Telegram alert: {e}")

