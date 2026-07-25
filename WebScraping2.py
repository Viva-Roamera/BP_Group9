## Linda - Zavvi LEGO price scraper - production script
## Shop selection process and rejected shops (LEGO.com, Coolblue) documented in shop_scraping_testing.py
## Limitations and future improvements on Zavvi: we identified Selenium/Playwright as a technical solution for JavaScript-rendered listings, but scoped it out given time constraints and chose manual curation instead.

import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import time
import csv
from pathlib import Path
from datetime import date

HEADERS = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}
DOMAIN = "https://www.zavvi.com"
CRAWL_DELAY_SECONDS = 10.0  # Zavvi's robots.txt gives no Crawl-delay, so I chose a conservative default

ZAVVI_PRODUCTS = [ 
    {"url": "https://www.zavvi.com/p/toys/lego-friends-horse-baby-foal-trailer-with-car-toy-42695/17650759/", "category": "Lego Friends"}, 
    {"url": "https://www.zavvi.com/p/toys/lego-city-airplane-service-truck-hovercraft-remix-60505/17650791/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-the-lego-van-toy-building-set-for-kids-60500/17650787/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-star-wars-cobb-vanth-s-speeder-toy-for-kids-75437/17650810/", "category": "Lego Star Wars"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-heartlake-city-friends-club-house-toy-42689/17650757/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-family-holiday-beach-resort-building-set-42673/16717297/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-horse-stable-and-riding-academy-toy-42688/17650756/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-beach-house-with-seals-building-toy-42699/17650761/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-heartlake-city-mini-supermarket-shop-toy-42680/17650750/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-fun-indoor-playground-toy-with-mini-dolls-42686/17650754/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-heartlake-city-fashion-show-toy-for-kids-42685/17650753/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-friends-animal-vet-clinic-with-toy-horse-stable-42696/17650760/", "category": "Lego Friends"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-snowplough-truck-toy-vehicle-with-minifigure-60490/17650783/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-coast-guard-rescue-boat-helicopter-playset-60504/17650790/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-coast-guard-helicopter-toy-building-set-60503/17650789/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-motorcycle-transporter-toy-and-2-minifigures-60491/17650784/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-holiday-adventure-camper-van-toy-vehicle-set-60454/15833871/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-airport-with-airplane-toy-model-airport-set-60502/17650788/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-city-yellow-taxi-model-car-kit-with-2-minifigures-60487/17650780/", "category": "Lego City"},
    {"url": "https://www.zavvi.com/p/toys/lego-star-wars-grogu-s-homestead-toy-building-set-75443/17650813/", "category": "Lego Star Wars"},
    {"url": "https://www.zavvi.com/p/toys/lego-star-wars-siege-of-mandalore-battle-pack-set-75449/17650815/", "category": "Lego Star Wars"},
    {"url": "https://www.zavvi.com/p/toys/lego-star-wars-clone-shock-trooper-mech-building-toy-75448/17650814/", "category": "Lego Star Wars"},
]


def get_zavvi_robots_parser():
    rp = RobotFileParser()
    rp.set_url(f"{DOMAIN}/robots.txt")
    robots_response = requests.get(f"{DOMAIN}/robots.txt", headers=HEADERS, timeout=10)
    rp.parse(robots_response.text.splitlines())
    return rp


def get_gbp_to_eur_rate() -> float:
    """Fetch today's GBP to EUR exchange rate from the European Central Bank via Frankfurter.app"""
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=GBP&to=EUR", timeout=10)
        response.raise_for_status()
        return response.json()["rates"]["EUR"]
    except (requests.RequestException, KeyError):
        print("  [!] Could not fetch live exchange rate, using fallback rate of 1.17")
        return 1.17  # approximate GBP->EUR rate as of mid-2026, documented fallback


def scrape_zavvi_product(url: str, category: str, rp: RobotFileParser, gbp_to_eur_rate: float) -> dict | None:
    if not rp.can_fetch(HEADERS["User-Agent"], url):
        print(f"  [skipped] robots.txt disallows: {url}")
        return None

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    name_tag = soup.find("h1", attrs={"data-testid": "pdp-product-title"})
    price_tag = soup.find("span", class_="pdp-price-text")

    if name_tag is None or price_tag is None:
        print(f"  [!] Couldn't find name/price on: {url}")
        return None

    price_gbp = float(price_tag.text.strip().replace("£", "").replace(",", ""))
    price_eur = round(price_gbp * gbp_to_eur_rate, 2)

    return {
        "shop": "Zavvi",
        "name": name_tag.text.strip(),
        "category": category,
        "price": price_eur,
        "url": url,
        "collection_date": date.today().isoformat(),
    }


def scrape_all_zavvi_products():
    """Loop through every product in ZAVVI_PRODUCTS, scrape each, pause between requests."""
    rp = get_zavvi_robots_parser()
    gbp_to_eur_rate = get_gbp_to_eur_rate()
    print(f"Using GBP to EUR rate: {gbp_to_eur_rate}")
    results = []

    for i, product in enumerate(ZAVVI_PRODUCTS, start=1):
        print(f"Fetching product {i} of {len(ZAVVI_PRODUCTS)}: {product['url']}")
        result = scrape_zavvi_product(product["url"], product["category"], rp, gbp_to_eur_rate)
        if result is not None:
            results.append(result)

        if i < len(ZAVVI_PRODUCTS):
            time.sleep(CRAWL_DELAY_SECONDS)

    return results


def save_zavvi_to_csv(products: list[dict], output_path: str = "zavvi_prices.csv"):
    """Write the collected product dictionaries to a CSV file."""
    out_path = Path(output_path)
    fieldnames = ["shop", "name", "category", "price", "url", "collection_date"]

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(products)

    print(f"\nSaved {len(products)} products to: {out_path}")


if __name__ == "__main__":
    products = scrape_all_zavvi_products()
    save_zavvi_to_csv(products)