# scrapers/scraper.py
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class Scraper:
    """
    A unified scraper for fetching data from websites using Selenium.
    """

    def __init__(self, selenium_hub_url: str):
        """
        Initializes the Scraper.

        Args:
            selenium_hub_url (str): The URL of the Selenium Grid hub.
        """
        self.selenium_hub_url = selenium_hub_url
        self.driver = self._create_driver()

    def _create_driver(self):
        """
        Creates and returns a WebDriver instance.
        If selenium_hub_url is "local", it creates a local Chrome driver.
        Otherwise, it creates a remote WebDriver.
        """
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            if self.selenium_hub_url == "local":
                # Use a local webdriver for E2E tests or local runs
                from selenium.webdriver.chrome.service import Service as ChromeService
                from webdriver_manager.chrome import ChromeDriverManager
                
                logging.info("Using local Chrome driver.")
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Use a remote webdriver for production (Docker) setup
                logging.info(f"Connecting to remote WebDriver at {self.selenium_hub_url}")
                driver = webdriver.Remote(
                    command_executor=self.selenium_hub_url,
                    options=options
                )
            return driver
        except WebDriverException as e:
            logging.error(f"Failed to create WebDriver: {e}")
            # This can happen if chromedriver is not found or grid is not available
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during WebDriver creation: {e}")
            return None

    def scrape(self, url: str, locator_info: dict) -> str:
        """
        Scrapes a single piece of data from the given URL.

        Args:
            url (str): The URL of the page to scrape.
            locator_info (dict): A dictionary containing 'by' and 'value' for the element locator.

        Returns:
            The text content of the found element, or "Error" if not found or on error.
        """
        if not self.driver:
            logging.error("WebDriver not available. Scraping aborted.")
            return "Error"
            
        try:
            self.driver.get(url)
            locator_method = getattr(By, locator_info['by'])
            wait = WebDriverWait(self.driver, 15) # Increased wait time for robustness
            
            # Wait for the element to be visible
            price_element = wait.until(
                EC.visibility_of_element_located((locator_method, locator_info['value']))
            )
            return price_element.text.strip()
        except TimeoutException:
            logging.error(f"Timeout while waiting for element at {url}")
            return "Error"
        except Exception as e:
            logging.error(f"An error occurred while scraping {url}: {e}")
            return "Error"

    def close(self):
        """Closes the WebDriver session."""
        if self.driver:
            self.driver.quit()
            self.driver = None # Ensure driver is cleared after quitting
