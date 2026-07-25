"""
WebScraping4.py
Melanie

Data source:
https://www.brickmo.com/en/lego/lego-icons/

This scraper collects only publicly available product information
(product name, price, number of pieces and product URL).

No personal data is collected.
The scraper respects robots.txt and includes a delay between requests
to avoid overloading the website.
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser


DOMAIN = "https://www.brickmo.com"

# Ethical crawling delay (seconds)
CRAWL_DELAY_SECONDS = 2


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}


def get_brickmo_robots_parser():
    """Load and parse the robots.txt file."""

    print("Loading robots.txt...")

    robots_url = f"{DOMAIN}/robots.txt"

    response = requests.get(
        robots_url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    rp = RobotFileParser()

    rp.parse(response.text.splitlines())

    print("robots.txt loaded successfully.")

    return rp



def scrape_page(url):

    # Check robots.txt before scraping
    rp = get_brickmo_robots_parser()

    can_scrape = rp.can_fetch(
        HEADERS["User-Agent"],
        url
    )

    print("Can scrape:", can_scrape)

    if not can_scrape:
        print(
            f"Scraping is not allowed according to robots.txt: {url}"
        )
        return []


    # Ethical crawling practice:
    # wait before requesting the website
    print(
        f"Waiting {CRAWL_DELAY_SECONDS} seconds..."
    )

    time.sleep(CRAWL_DELAY_SECONDS)


    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    print("Status:", response.status_code)


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    products = []


    product_boxes = soup.find_all(
        "div",
        class_="product--box"
    )


    print(
        "Products found:",
        len(product_boxes)
    )


    for product in product_boxes:

        name = product.find(
            "a",
            class_="product--title"
        )

        price = product.find(
            "span",
            class_="price--default"
        )

        pieces = product.find(
            "div",
            class_="list-bricks"
        )


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


        # Save product data
        if name:

            products.append(
                {
                    "shop": "Brickmo",
                    "name": name.get_text(strip=True),
                    "price": price_text,
                    "pieces": pieces_text,
                    "url": name.get("href")
                }
            )


    return products



if __name__ == "__main__":

    url = (
        "https://www.brickmo.com/en/lego/lego-icons/"
    )


    products = scrape_page(url)


    df = pd.DataFrame(products)


    df.to_csv(
        "brickmo_prices.csv",
        index=False,
        encoding="utf-8-sig"
    )


    print(
        f"\n{len(products)} products saved to brickmo_prices.csv"
    )