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

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

from scraping_policy import RobotsPolicy, USER_AGENT

DOMAIN = "https://www.brickmo.com"

HEADERS = {"User-Agent": USER_AGENT}



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



def scrape_page(url, policy):
    products = []

    page_url = url

    seen_pages = set()


    while page_url:


        if page_url in seen_pages:
            break


        seen_pages.add(page_url)

        # Pagination URLs can have different robots rules, so check every page.
        if not policy.can_fetch(page_url):
            break

        policy.wait_before_request()
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

    policy = RobotsPolicy(DOMAIN)

    urls = [
        "https://www.brickmo.com/en/lego/lego-city/",
        "https://www.brickmo.com/en/lego/lego-star-wars/",
        "https://www.brickmo.com/en/lego/lego-friends/",
        "https://www.brickmo.com/en/lego/lego-icons/"
    ]

    all_products = []

    for url in urls:

        products = scrape_page(url, policy)

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
