"""
Melanie - Brickmo.com - Product Price Scraper
==============================================

Website:
    https://www.brickmo.com/

Purpose:
    Scrapes product names and prices from category/listing pages
    for competitor price monitoring.

Output:
    Product name, price, and related product information.
"""

import requests
from bs4 import BeautifulSoup


def scrape_page(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)

    print("Status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    product_boxes = soup.find_all("div", class_="product--box")

    print("Products found:", len(product_boxes))

    for product in product_boxes:

        # Find the product information
        name = product.find("a", class_="product--title")
        price = product.find("span", class_="price--default")
        pieces = product.find("div", class_="list-bricks")

        # Clean the price
        price_text = ""

        if price:
            price_text = (
                price.get_text(" ", strip=True)
                .replace("\xa0", "")
                .replace("€", "")
                .replace("*", "")
                .strip()
            )

        # Clean the number of pieces
        pieces_text = ""

        if pieces:
            pieces_text = (
                pieces.get_text(strip=True)
                .replace("Teile", "")
                .strip()
            )

        # Save the product
        if name:
            products.append({
                "shop": "Brickmo",
                "name": name.get_text(strip=True),
                "price": price_text,
                "pieces": pieces_text,
                "url": name["href"]
            })

    return products

