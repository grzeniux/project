# Project Overview
Projekt do portfolio QA Automation. Cel: automatyczne śledzenie cen aktywów finansowych i raportowanie błędów.

# Tech Stack
- Python 3.9+
- Selenium WebDriver (tryb Remote/Headless)
- Docker & Docker Compose
- Pytest (do testów dymnych)

# Scope of Work (Assets to Track)
- Crypto: BTC/USDT, ETH/USDT (np. z Binance/CoinMarketCap)
- Stocks: S&P 500, WIG 20, DINO (np. z Bankier/Stooq)
- Commodities: Złoto

# QA Engineering Standards (CRITICAL)
- Stosowanie wyłącznie Explicit Waits (WebDriverWait). Zakaz używania `time.sleep()`.
- Obsługa wyjątków: Każdy błąd musi generować zrzut ekranu (screenshot) zapisywany w wolumenie `/logs`.
- Czysty kod: Użycie klasy bazowej `BaseScraper` i dziedziczenie.

# Infrastructure & Architecture
- Kontener 1: Aplikacja Python (Scraper).
- Kontener 2: `selenium/standalone-chrome` (oficjalny obraz Docker).
- Komunikacja: Python łączy się z Chrome przez port 4444.

# Current Status
Struktura folderów jest utworzona, a następnym krokiem jest implementacja logiki scraperów.
