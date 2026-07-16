"""
## Iva - BricksDirect.com - product price scraper
Note: Need to install the following packages if not already installed:
    pip install pandas beautifulsoup4 requests
============================================
Scrapes product name + price from listing/category pages on
https://bricksdirect.com/

Price is read from:
    <span class="price product-price" aria-label="Price"> €22.80 </span>

Responsible scraping:
  - CRAWL_DELAY_SECONDS is set to 10 seconds between requests, as defined in bricksdirect.com/robots.txt
    first.
  - Only reads publicly listed catalog/category pages (GET requests).
  - Sends a normal browser User-Agent; does not bypass any login/paywall.

Output:
  - CSV file written to OUTPUT_PATH: bricksdirect_prices.csv
"""

import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# CONFIG 
# ----------------------------------------------------------------------
START_URLS = [
    "https://bricksdirect.com/lego-city", "https://bricksdirect.com/lego-star-wars", "https://bricksdirect.com/lego-friends"
    # Add more category/listing page URLs here, e.g.:
    # "https://bricksdirect.com/collections/lego-star-wars",
]
MAX_PAGES_PER_CATEGORY = 5       # how many paginated pages to follow per start URL
CRAWL_DELAY_SECONDS = 10.0       # required delay between requests

# Save the CSV in the same folder as this script, whatever machine it runs on.
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = SCRIPT_DIR / "bricksdirect_prices.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IE,en;q=0.9",
}


def get_soup(url: str, session: requests.Session) -> BeautifulSoup | None:
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print(f"  [!] Failed to fetch {url}: {exc}")
        return None


def clean_price(text: str):
    """'€22.80' / '22,80 €' -> 22.80 (float), currency symbol kept separately."""
    if not text:
        return None, None
    text = text.strip()
    currency_match = re.search(r"[€]", text)
    currency = currency_match.group(0) if currency_match else None
    number_match = re.search(r"[\d.,]+", text)
    if not number_match:
        return None, currency
    number_str = number_match.group(0).replace(",", "")
    try:
        return float(number_str), currency
    except ValueError:
        return None, currency


def extract_category(soup: BeautifulSoup) -> str:
    heading = soup.select_one('h1.page-heading.js-category-page')
    if heading:
        text = heading.get_text(" ", strip=True)
        if text:
            return text
    return ""


def parse_products(soup: BeautifulSoup) -> list[dict]:
    """
    Extract product cards using the price span as the anchor:
        <span class="price product-price" aria-label="Price"> €22.80 </span>
    """
    products = []
    category = extract_category(soup)
    price_spans = soup.select('span.price.product-price[aria-label="Price"]')

    for price_span in price_spans:
        price, currency = clean_price(price_span.get_text())

        # Walk up to the product card container (has a link + likely a title).
        card = price_span.find_parent(
            lambda tag: tag.name in ("div", "li", "article")
            and tag.find("a", href=True) is not None
        )
        if card is None:
            card = price_span.parent

        # Product name/link: BricksDirect product cards use a pattern like
        #   <a href="https://bricksdirect.com/lego-77261-ferrari-499p"
        #      title="LEGO 77261 Ferrari 499P">LEGO 77261 Ferrari 499P</a>
        # Prefer this a[title][href] link since both its `title` attribute
        # and its text give a clean product name.
        name = None
        link_tag = None
        if card is not None:
            name_link = card.find("a", href=True, title=True)
            if name_link is not None:
                link_tag = name_link
                # Prefer the title attribute (kept clean even if the link
                # text is later wrapped in extra spans/images).
                name = name_link.get("title", "").strip() or name_link.get_text(strip=True)

        if name is None and card is not None:
            name_tag = (
                card.find(["h2", "h3"])
                or card.find(class_=re.compile("title|name", re.I))
                or card.find("a", href=True)
            )
            name = name_tag.get_text(strip=True) if name_tag else None
            if link_tag is None:
                link_tag = card.find("a", href=True)

        if link_tag is None and card is not None:
            link_tag = card.find("a", href=True)

        product_url = link_tag["href"] if link_tag else None
        if product_url and product_url.startswith("/"):
            product_url = "https://bricksdirect.com" + product_url

        products.append(
            {
                "category": category,
                "name": name,
                "price": price,
                "currency": currency,
                "url": product_url,
            }
        )

    return products


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    """Look for a 'next page' link. Adjust selector if the site's pagination
    markup differs from this common pattern."""
    next_link = soup.select_one('a[rel="next"], a.pagination-next, a[aria-label="Next"]')
    if next_link and next_link.get("href"):
        href = next_link["href"]
        if href.startswith("/"):
            return "https://bricksdirect.com" + href
        return href
    return None


def scrape_all() -> list[dict]:
    all_products = []
    seen_urls = set()

    with requests.Session() as session:
        for start_url in START_URLS:
            url = start_url
            for page_num in range(1, MAX_PAGES_PER_CATEGORY + 1):
                print(f"Fetching page {page_num} of {start_url}: {url}")
                soup = get_soup(url, session)
                if soup is None:
                    break

                page_products = parse_products(soup)
                new_count = 0
                for p in page_products:
                    key = p["url"] or p["name"]
                    if key and key not in seen_urls:
                        seen_urls.add(key)
                        all_products.append(p)
                        new_count += 1

                print(f"  Found {len(page_products)} products ({new_count} new).")

                if not page_products:
                    print("  No products found — page may be JS-rendered, or "
                          "this URL isn't a product listing page.")
                    break

                next_url = find_next_page_url(soup, url)
                # Required crawl delay before the next request (final page or not)
                time.sleep(CRAWL_DELAY_SECONDS)

                if not next_url or next_url == url:
                    break
                url = next_url

    return all_products


def save_to_csv(products: list[dict], output_path: str) -> None:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["category", "name", "price", "currency", "url"]
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    print(f"\nSaved {len(products)} products to: {out_path}")


def main():
    products = scrape_all()
    if not products:
        print(
            "\nNo products were extracted."
        )
        return

    save_to_csv(products, output_path=OUTPUT_PATH)


if __name__ == "__main__":
    main()