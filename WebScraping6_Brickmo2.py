"""
## Iva - TEST Brickmo (WebScraping4) extended product themes + Category - product price scraper
Output: brickmo2_prices.csv
Note: Need to install the following packages if not already installed:
    pip install pandas beautifulsoup4 requests
============================================
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

def extract_category(url, soup):
    # Primary: derive the category straight from the URL slug.
    # This is reliable because BRICKMO's category URLs already map
    # cleanly to category names (e.g. /lego/lego-icons/ -> "Lego Icons").
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    ignored_parts = {"en", "de", "fr", "nl", "it", "es", "pl", "cs", "hu", "uk", "ru", "lego"}
    for part in reversed(path_parts):
        if part.lower() not in ignored_parts:
            return part.replace("-", " ").replace("_", " ").title()

    # Fallback: only used if the URL didn't yield a usable category
    # (e.g. an unexpected URL structure). Note this can be unreliable
    # on pages that also contain other itemprop="name"/breadcrumb--title
    # elements elsewhere on the page (such as "New at BRICKMO" widgets),
    # since select_one() will grab whichever one appears first in the HTML.
    breadcrumb = soup.select_one('span.breadcrumb--title, span[itemprop="name"]')
    if breadcrumb:
        text = breadcrumb.get_text(" ", strip=True)
        if text:
            return text

    return ""


def scrape_page(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        )
    }

    products = []
    page_url = url
    seen_pages = set()

    while page_url:
        if page_url in seen_pages:
            break
        seen_pages.add(page_url)

        response = requests.get(page_url, headers=headers, timeout=20)
        print("Status:", response.status_code, "Page:", page_url)

        if response.status_code != 200:
            print("Skipping this URL because the page did not return 200.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        product_boxes = soup.find_all("div", class_="product--box")
        print("Products found on this page:", len(product_boxes))

        category = extract_category(page_url, soup)

        for product in product_boxes:
            # Find product information
            name = product.find("a", class_="product--title")
            price = product.find("span", class_="price--default")
            pieces = product.find("div", class_="list-bricks")

            # Clean price
            price_text = ""

            if price:
                price_text = (
                    price.get_text(" ", strip=True)
                    .replace("\xa0", "")
                    .replace("€", "")
                    .replace("*", "")
                    .strip()
                )

            # Clean pieces
            pieces_text = ""

            if pieces:
                pieces_text = (
                    pieces.get_text(strip=True)
                    .replace("Teile", "")
                    .replace("Pieces", "")
                    .strip()
                )

            # Save product
            if name:
                products.append({
                    "shop": "Brickmo",
                    "category": category,
                    "name": name.get_text(strip=True),
                    "price": price_text,
                    ##"pieces": pieces_text,
                    "url": name["href"],
                    "collection_date": datetime.now().strftime("%Y-%m-%d"),
                })

        next_page = None
        for link in soup.select("a[href]"):
            href = link.get("href", "")
            if href and "?p=" in href:
                next_page = urljoin(page_url, href)
                break

        if not next_page or next_page in seen_pages:
            break

        page_url = next_page

    return products


if __name__ == "__main__":

    urls = [
        "https://www.brickmo.com/en/lego/lego-city/",
        "https://www.brickmo.com/en/lego/lego-star-wars/",
        "https://www.brickmo.com/en/lego/lego-friends/",
        "https://www.brickmo.com/en/lego/lego-icons/"
    ]
    all_products = []

    for url in urls:
        products = scrape_page(url)
        all_products.extend(products)

    # Convert to DataFrame
    df = pd.DataFrame(all_products)

    # Save CSV in the current folder
    df.to_csv(
        "brickmo2_prices.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n{len(all_products)} products saved to brickmo2_prices.csv")