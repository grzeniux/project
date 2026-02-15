# main.py
import json
import time
import logging
from scrapers.scraper import Scraper
from scrapers.notifications import TelegramNotifier

def load_json(filename):
    """Safely load a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {filename}: {e}")
        return None

def clean_price(price_str):
    """
    Cleans a price string by removing commas and other non-numeric characters,
    then converts it to a float.
    """
    if price_str is None or price_str == "Error":
        return None
    
    cleaned_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
    try:
        return float(cleaned_str)
    except (ValueError, TypeError):
        logging.error(f"Could not convert string to float: {price_str}")
        return None

def check_alerts(asset_name, price, alerts_config, notifier):
    """Check if the price triggers any alerts."""
    if asset_name not in alerts_config:
        return

    alert_conditions = alerts_config[asset_name]
    message = None

    if "above" in alert_conditions and price > alert_conditions["above"]:
        message = f"🔔 ALERT for {asset_name} 🔔\nPrice is ABOVE {alert_conditions['above']} at {price}"
    
    if "below" in alert_conditions and price < alert_conditions["below"]:
        message = f"🔔 ALERT for {asset_name} 🔔\nPrice is BELOW {alert_conditions['below']} at {price}"

    if message:
        notifier.send_alert(message)

def main():
    """
    Main function to run the scraper periodically.
    """
    config = load_json('config.json')
    if not config:
        logging.critical("Could not load config.json. Application cannot start.")
        return

    # Extract settings from config
    settings = config.get('settings', {})
    assets_to_track = config.get('assets', {})
    alerts_config = config.get('alerts', {})
    locator_info = config.get('locators', {}).get('tradingview.com')

    interval = settings.get('scraping_interval_seconds', 900)
    selenium_hub_url = settings.get('selenium_hub_url')

    if not all([assets_to_track, alerts_config, locator_info, selenium_hub_url]):
        logging.critical("Configuration is incomplete. Missing assets, alerts, locators, or selenium_hub_url.")
        return

    notifier = TelegramNotifier()
    scraper = Scraper(selenium_hub_url)

    notifier.send_alert("🚀 Scraper wystartował i rozpoczyna cykliczne sprawdzanie cen.")

    try:
        while True:
            logging.info("Rozpoczynam sprawdzanie cen...")

            for category, assets in assets_to_track.items():
                for asset_name, asset_details in assets.items():
                    url = asset_details.get('url')
                    if not url:
                        logging.warning(f"URL not found for asset: {asset_name}")
                        continue

                    scraped_price_str = scraper.scrape(url, locator_info)
                    price = clean_price(scraped_price_str)
                    
                    message = f"Cena dla {asset_name}: {price if price is not None else 'Error'}"
                    print(message)
                    logging.info(message)
                    
                    if price is not None:
                        check_alerts(asset_name, price, alerts_config, notifier)
            
            logging.info(f"Zakończono sprawdzanie. Następne za {interval} sekund.")
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Otrzymano polecenie zamknięcia. Kończenie pracy...")
    finally:
        scraper.close()
        logging.info("Scraper zamknięty. Do widzenia!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
