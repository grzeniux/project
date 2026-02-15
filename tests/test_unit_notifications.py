# tests/test_unit_notifications.py
import pytest
from scrapers.notifications import TelegramNotifier

def test_telegram_notifier_send_alert_success(mocker):
    """
    Test that TelegramNotifier.send_alert calls requests.post with the correct parameters
    when the notifier is properly configured.
    """
    # Mock os.getenv to simulate configured environment variables
    mocker.patch('os.getenv', side_effect=lambda key: {'TELEGRAM_TOKEN': 'fake_token', 'TELEGRAM_CHAT_ID': 'fake_chat_id'}.get(key))
    
    # Mock requests.post
    mock_post = mocker.patch('requests.post')
    
    # Initialize the notifier and send an alert
    notifier = TelegramNotifier()
    notifier.send_alert("Test message")
    
    # Assert that requests.post was called once with the correct URL and payload
    expected_url = "https://api.telegram.org/botfake_token/sendMessage"
    expected_payload = {
        "chat_id": "fake_chat_id",
        "text": "Test message",
        "parse_mode": "Markdown"
    }
    mock_post.assert_called_once_with(expected_url, json=expected_payload, timeout=10)

def test_telegram_notifier_send_alert_not_configured(mocker):
    """
    Test that TelegramNotifier.send_alert does not call requests.post
    when the notifier is not configured (missing environment variables).
    """
    # Mock os.getenv to simulate missing environment variables
    mocker.patch('os.getenv', return_value=None)
    
    # Mock requests.post
    mock_post = mocker.patch('requests.post')
    
    # Initialize the notifier and attempt to send an alert
    notifier = TelegramNotifier()
    notifier.send_alert("Test message")
    
    # Assert that requests.post was not called
    mock_post.assert_not_called()

def test_telegram_notifier_init_warning_not_configured(mocker, caplog):
    """
    Test that a warning is logged during initialization if the notifier is not configured.
    """
    # Mock os.getenv to simulate missing environment variables
    mocker.patch('os.getenv', return_value=None)
    
    # Initialize the notifier
    TelegramNotifier()
    
    # Assert that the expected warning message is in the logs
    assert "Telegram token or chat ID not set. Notifications are disabled." in caplog.text
