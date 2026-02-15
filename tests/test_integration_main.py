# tests/test_integration_main.py
import pytest
from unittest.mock import MagicMock
from main import check_alerts, main

@pytest.fixture
def mock_notifier():
    """Fixture to create a mock TelegramNotifier."""
    notifier = MagicMock()
    # We need to create a mock for the send_alert method on the instance
    notifier.send_alert = MagicMock()
    return notifier

def test_check_alerts_price_above_triggers_alert(mock_notifier):
    """
    Test that an alert is triggered when the price goes ABOVE the configured threshold.
    """
    asset_name = "BTC"
    price = 50000
    alerts_config = {"BTC": {"above": 48000}}
    
    check_alerts(asset_name, price, alerts_config, mock_notifier)
    
    expected_message = f"🔔 ALERT for {asset_name} 🔔\nPrice is ABOVE {alerts_config[asset_name]['above']} at {price}"
    mock_notifier.send_alert.assert_called_once_with(expected_message)

def test_check_alerts_price_below_triggers_alert(mock_notifier):
    """
    Test that an alert is triggered when the price goes BELOW the configured threshold.
    """
    asset_name = "ETH"
    price = 2800
    alerts_config = {"ETH": {"below": 3000}}
    
    check_alerts(asset_name, price, alerts_config, mock_notifier)
    
    expected_message = f"🔔 ALERT for {asset_name} 🔔\nPrice is BELOW {alerts_config[asset_name]['below']} at {price}"
    mock_notifier.send_alert.assert_called_once_with(expected_message)

def test_check_alerts_no_condition_met(mock_notifier):
    """
    Test that no alert is sent if the price is within the dead zone (not above or below).
    """
    asset_name = "BTC"
    price = 45000
    alerts_config = {"BTC": {"above": 48000, "below": 40000}}
    
    check_alerts(asset_name, price, alerts_config, mock_notifier)
    
    mock_notifier.send_alert.assert_not_called()

def test_check_alerts_no_config_for_asset(mock_notifier):
    """
    Test that no alert is sent if there is no alert configuration for the given asset.
    """
    asset_name = "DOGE"
    price = 0.15
    alerts_config = {"BTC": {"above": 48000}} # No config for DOGE
    
    check_alerts(asset_name, price, alerts_config, mock_notifier)
    
    mock_notifier.send_alert.assert_not_called()

def test_main_loop_sends_alert_on_price_change(mocker):
    """
    Test the main application loop to ensure it scrapes prices and sends alerts.
    This is a larger integration test that mocks all external services.
    """
    # 1. Mock configuration and external services
    mock_load_json = mocker.patch('main.load_json')
    mock_scraper_class = mocker.patch('main.Scraper')
    mock_notifier_class = mocker.patch('main.TelegramNotifier')
    mock_sleep = mocker.patch('time.sleep')

    # 2. Define the mock configuration
    mock_config = {
        "settings": {
            "scraping_interval_seconds": 1,
            "selenium_hub_url": "http://fake-hub:4444"
        },
        "assets": {
            "CRYPTO": {
                "BTC": {"url": "http://fake-url.com/btc"}
            }
        },
        "alerts": {
            "BTC": {"below": 60000}
        },
        "locators": {
            "tradingview.com": {"by": "CLASS_NAME", "value": "price"}
        }
    }
    mock_load_json.return_value = mock_config

    # 3. Configure the mock scraper instance
    mock_scraper_instance = MagicMock()
    # Let's simulate the price dropping
    mock_scraper_instance.scrape.side_effect = ["65000.00", "59000.00"] 
    mock_scraper_class.return_value = mock_scraper_instance

    # 4. Configure the mock notifier instance
    mock_notifier_instance = MagicMock()
    mock_notifier_class.return_value = mock_notifier_instance

    # 5. We need to stop the infinite loop. We'll patch `time.sleep` to raise an exception
    # after a few calls, which will exit the `while True` loop.
    mock_sleep.side_effect = [None, KeyboardInterrupt] # First call sleeps, second one stops the loop

    # 6. Run the main function
    try:
        main()
    except KeyboardInterrupt:
        pass # We expect this to happen to stop the loop

    # 7. Assertions
    # Check that the startup alert was sent
    mock_notifier_instance.send_alert.assert_any_call("🚀 Scraper wystartował i rozpoczyna cykliczne sprawdzanie cen.")

    # Check that the scraper was called twice
    assert mock_scraper_instance.scrape.call_count == 2
    
    # Check that the price drop triggered an alert
    expected_alert_message = "🔔 ALERT for BTC 🔔\nPrice is BELOW 60000 at 59000.0"
    mock_notifier_instance.send_alert.assert_any_call(expected_alert_message)
    
    # Check that the scraper was closed
    mock_scraper_instance.close.assert_called_once()
