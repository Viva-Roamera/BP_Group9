## Linda - Zavvi LEGO price scraper - production script
## Shop selection process and rejected shops (LEGO.com, Coolblue) documented in local file shop_scraping_testing.py

import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import time
import csv
from pathlib import Path
from datetime import date

HEADERS = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}
DOMAIN = "https://www.zavvi.com"
CRAWL_DELAY_SECONDS = 10.0  ## Zavvi's robots.txt gives no Crawl-delay, so I chose a conservative default

ZAVVI_PRODUCT_URLS = [
    "https://www.zavvi.com/p/toys-lego/lego-mindstorms-ev3-robot-coding-robotics-kit-31313/10757770/",
    "https://www.zavvi.com/p/toys/lego-speed-champions-ferrari-sf90-xx-stradale-sports-car-77254/17650840/",
    ## Add more Zavvi product page URLs here as the set list gets finalised
]

def get_zavvi_robots_parser():
    rp = RobotFileParser()
    rp.set_url(f"{DOMAIN}/robots.txt")
    robots_response = requests.get(f"{DOMAIN}/robots.txt", headers=HEADERS, timeout=10)
    rp.parse(robots_response.text.splitlines())
    return rp


def scrape_zavvi_product(url: str, rp: RobotFileParser) -> dict | None:
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

    return {
        "name": name_tag.text.strip(),
        "shop": "Zavvi",
        "url": url,
        "price": price_tag.text.strip(),
        "collection_date": date.today().isoformat(),
    }


def scrape_all_zavvi_products():
    """Loop through every URL in ZAVVI_PRODUCT_URLS, scrape each, pause between requests."""
    rp = get_zavvi_robots_parser()
    results = []

    for i, url in enumerate(ZAVVI_PRODUCT_URLS, start=1):
        print(f"Fetching product {i} of {len(ZAVVI_PRODUCT_URLS)}: {url}")
        product = scrape_zavvi_product(url, rp)
        if product is not None:
            results.append(product)

        if i < len(ZAVVI_PRODUCT_URLS):
            time.sleep(CRAWL_DELAY_SECONDS)

    return results


def save_zavvi_to_csv(products: list[dict], output_path: str = "zavvi_prices.csv"):
    """Write the collected product dictionaries to a CSV file."""
    out_path = Path(output_path)
    fieldnames = ["name", "shop", "url", "price", "collection_date"]

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(products)

    print(f"\nSaved {len(products)} products to: {out_path}")


if __name__ == "__main__":
    products = scrape_all_zavvi_products()
    save_zavvi_to_csv(products)