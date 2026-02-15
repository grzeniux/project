# tests/test_unit_scraper.py
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException, WebDriverException
from scrapers.scraper import Scraper

@pytest.fixture
def mock_webdriver():
    """Fixture to mock the webdriver.Remote."""
    with patch('selenium.webdriver.Remote') as mock_remote:
        # We mock the entire webdriver.Remote class
        mock_driver_instance = MagicMock()
        mock_remote.return_value = mock_driver_instance
        yield mock_remote, mock_driver_instance

def test_scraper_init(mock_webdriver):
    """Test that the Scraper initializes the webdriver correctly."""
    mock_remote, _ = mock_webdriver
    Scraper("http://fake-hub:4444/wd/hub")
    
    # Assert that webdriver.Remote was called
    mock_remote.assert_called_once()
    
    # Check if it was called with an options object
    args, kwargs = mock_remote.call_args
    assert 'options' in kwargs
    options = kwargs['options']
    assert "--headless" in options.arguments
    assert "--no-sandbox" in options.arguments
    assert "--disable-dev-shm-usage" in options.arguments

def test_scraper_init_webdriver_exception(caplog):
    """Test that an error is logged if WebDriver creation fails."""
    with patch('selenium.webdriver.Remote', side_effect=WebDriverException("Failed to connect")):
        scraper = Scraper("http://fake-hub:4444/wd/hub")
        assert scraper.driver is None
        assert "Failed to create WebDriver" in caplog.text

def test_scraper_scrape_success(mock_webdriver):
    """Test the successful scraping of an element."""
    _, mock_driver_instance = mock_webdriver
    
    # Configure the mock driver to simulate finding an element
    mock_element = MagicMock()
    mock_element.text = " 123.45 "
    
    # The wait object will return our mock element
    mock_wait = MagicMock()
    mock_wait.until.return_value = mock_element
    
    with patch('scrapers.scraper.WebDriverWait', return_value=mock_wait) as mock_WebDriverWait:
        scraper = Scraper("http://fake-hub:4444/wd/hub")
        
        # Call the scrape method
        result = scraper.scrape("http://fake-url.com", {'by': 'CLASS_NAME', 'value': 'price'})
        
        # Assertions
        assert result == "123.45"
        mock_driver_instance.get.assert_called_once_with("http://fake-url.com")
        mock_WebDriverWait.assert_called_once()
        mock_wait.until.assert_called_once()

def test_scraper_scrape_timeout(mock_webdriver, caplog):
    """Test that the scraper handles a TimeoutException correctly."""
    _, mock_driver_instance = mock_webdriver
    
    # Configure the wait object to raise a TimeoutException
    mock_wait = MagicMock()
    mock_wait.until.side_effect = TimeoutException("Element not found")
    
    with patch('scrapers.scraper.WebDriverWait', return_value=mock_wait):
        scraper = Scraper("http://fake-hub:4444/wd/hub")
        result = scraper.scrape("http://fake-url.com", {'by': 'ID', 'value': 'price'})
        
        # Assertions
        assert result == "Error"
        assert "Timeout while waiting for element" in caplog.text

def test_scraper_close(mock_webdriver):
    """Test that the close method quits the driver."""
    _, mock_driver_instance = mock_webdriver
    scraper = Scraper("http://fake-hub:4444/wd/hub")
    
    scraper.close()
    
    # Assert that quit was called and driver is set to None
    mock_driver_instance.quit.assert_called_once()
    assert scraper.driver is None

def test_scrape_with_no_driver(caplog):
    """Test that scrape handles cases where the driver failed to initialize."""
    with patch('selenium.webdriver.Remote', side_effect=WebDriverException("Connection refused")):
        scraper = Scraper("http://fake-hub:4444/wd/hub")
        result = scraper.scrape("http://fake-url.com", {'by': 'ID', 'value': 'price'})
        
        assert result == "Error"
        assert "WebDriver not available. Scraping aborted." in caplog.text
