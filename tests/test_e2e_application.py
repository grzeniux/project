# tests/test_e2e_application.py
import json
import os
import pytest
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler
from unittest.mock import MagicMock

# --- Test Setup: HTTP Server ---

class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress log messages

@pytest.fixture(scope="module")
def local_http_server():
    """Fixture to run a simple HTTP server in a background thread to serve a test page."""
    host, port = "localhost", 8081
    
    class Handler(QuietHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # Serve files from the 'tests/test_data' directory
            super().__init__(*args, directory=os.path.join(os.getcwd(), 'tests', 'test_data'), **kwargs)

    httpd = HTTPServer((host, port), Handler)
    
    server_thread = Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    
    yield f"http://{host}:{port}/e2e_page.html"
    
    httpd.shutdown()
    server_thread.join()

# --- E2E Test ---

@pytest.mark.e2e
def test_e2e_in_process_application_run(mocker, local_http_server, capsys):
    """
    A hybrid E2E test that runs the main application logic in-process.
    - It uses a real local webdriver to scrape a page from a real local HTTP server.
    - It mocks external services like notifications and the main loop's sleep.
    """
    # 1. Mock configuration and external services
    mock_load_json = mocker.patch('main.load_json')
    mock_notifier_class = mocker.patch('main.TelegramNotifier')
    mock_sleep = mocker.patch('time.sleep')

    # 2. Define the mock configuration to use the local scraper and server
    mock_config = {
        "settings": {
            "scraping_interval_seconds": 1,
            "selenium_hub_url": "local"  # Use local Chrome driver
        },
        "assets": {
            "E2E": {
                "TestAsset": {"url": local_http_server}
            }
        },
        "alerts": {
            "TestAsset": {"below": 1000}
        },
        "locators": {
            # This key is not ideal, but we adapt to the current config structure
            "tradingview.com": {"by": "CLASS_NAME", "value": "price-class"}
        }
    }
    mock_load_json.return_value = mock_config

    # 3. Configure mock notifier and the loop-stopping mechanism
    mock_notifier_instance = MagicMock()
    mock_notifier_class.return_value = mock_notifier_instance

    # This generator stops the main loop on the first call to time.sleep
    # and allows subsequent calls that might occur during cleanup (e.g., in driver.quit()).
    def sleep_generator():
        yield KeyboardInterrupt
        while True:
            yield None

    mock_sleep.side_effect = sleep_generator()

    # 4. Run the main application
    from main import main
    main()

    # 5. Assertions
    captured = capsys.readouterr()
    # Check that the application logged the scraping result to stdout
    assert "Cena dla TestAsset: 999.99" in captured.out
    
    # Check that the price triggered an alert
    expected_alert_message = "🔔 ALERT for TestAsset 🔔\nPrice is BELOW 1000 at 999.99"
    mock_notifier_instance.send_alert.assert_any_call(expected_alert_message)