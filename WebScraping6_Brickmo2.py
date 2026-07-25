"""
## Iva - TEST Brickmo (WebScraping6)
Extended product themes + category + product price scraper

Output:
brickmo2_prices.csv

Melanie - Ethical scraping:
- Checks robots.txt before scraping
- Uses crawl delay between requests
- Collects only publicly available product information

Install packages if needed:
pip install pandas beautifulsoup4 requests

============================================
"""

import requests
import pandas as pd
import time

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from datetime import datetime


DOMAIN = "https://www.brickmo.com"

CRAWL_DELAY_SECONDS = 2


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}



def get_robots_parser(domain):
    """
    Load and parse robots.txt.
    """

    print("Loading robots.txt...")

    robots_url = f"{domain}/robots.txt"

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



def extract_category(url, soup):

    # Primary: derive category from URL
    path_parts = [
        part for part in urlparse(url).path.split("/")
        if part
    ]

    ignored_parts = {
        "en",
        "de",
        "fr",
        "nl",
        "it",
        "es",
        "pl",
        "cs",
        "hu",
        "uk",
        "ru",
        "lego"
    }

    for part in reversed(path_parts):

        if part.lower() not in ignored_parts:

            return (
                part
                .replace("-", " ")
                .replace("_", " ")
                .title()
            )


    # Fallback
    breadcrumb = soup.select_one(
        'span.breadcrumb--title, span[itemprop="name"]'
    )

    if breadcrumb:

        text = breadcrumb.get_text(
            " ",
            strip=True
        )

        if text:
            return text


    return ""



def scrape_page(url, rp):

    # Check robots.txt before scraping

    can_scrape = rp.can_fetch(
        HEADERS["User-Agent"],
        url
    )

    print("Can scrape:", can_scrape)


    if not can_scrape:

        print(
            f"Scraping not allowed by robots.txt: {url}"
        )

        return []


    products = []

    page_url = url

    seen_pages = set()


    while page_url:


        if page_url in seen_pages:
            break


        seen_pages.add(page_url)


        # Ethical crawling delay
        print(
            f"Waiting {CRAWL_DELAY_SECONDS} seconds..."
        )

        time.sleep(CRAWL_DELAY_SECONDS)


        response = requests.get(
            page_url,
            headers=HEADERS,
            timeout=20
        )


        print(
            "Status:",
            response.status_code,
            "Page:",
            page_url
        )


        if response.status_code != 200:

            print(
                "Skipping this URL because the page did not return 200."
            )

            break



        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        product_boxes = soup.find_all(
            "div",
            class_="product--box"
        )


        print(
            "Products found on this page:",
            len(product_boxes)
        )


        category = extract_category(
            page_url,
            soup
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
                    price.get_text(
                        " ",
                        strip=True
                    )
                    .replace("\xa0", "")
                    .replace("€", "")
                    .replace("*", "")
                    .strip()
                )



            # Clean pieces

            pieces_text = ""

            if pieces:

                pieces_text = (
                    pieces.get_text(
                        strip=True
                    )
                    .replace("Teile", "")
                    .replace("Pieces", "")
                    .strip()
                )



            if name:

                products.append(
                    {
                        "shop": "Brickmo",
                        "category": category,
                        "name": name.get_text(
                            strip=True
                        ),
                        "price": price_text,
                        "pieces": pieces_text,
                        "url": urljoin(
                            page_url,
                            name.get("href")
                        ),
                        "collection_date": datetime.now().strftime(
                            "%Y-%m-%d"
                        )
                    }
                )



        # Find next page

        next_page = None


        for link in soup.select("a[href]"):

            href = link.get(
                "href",
                ""
            )

            if href and "?p=" in href:

                next_page = urljoin(
                    page_url,
                    href
                )

                break



        if not next_page or next_page in seen_pages:

            break


        page_url = next_page



    return products





if __name__ == "__main__":

    rp = get_robots_parser(DOMAIN)

    urls = [
        "https://www.brickmo.com/en/lego/lego-city/",
        "https://www.brickmo.com/en/lego/lego-star-wars/",
        "https://www.brickmo.com/en/lego/lego-friends/",
        "https://www.brickmo.com/en/lego/lego-icons/"
    ]

    all_products = []

    for url in urls:

        products = scrape_page(url, rp)

        all_products.extend(products)


    df = pd.DataFrame(all_products)


    df.to_csv(
        "brickmo2_prices.csv",
        index=False,
        encoding="utf-8-sig"
    )


    print(
        f"\n{len(all_products)} products saved to brickmo2_prices.csv"
    )