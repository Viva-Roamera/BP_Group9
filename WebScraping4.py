import requests
import pandas as pd
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
                "name": name.get_text(strip=True),
                "price": price_text,
                "pieces": pieces_text,
                "url": name["href"]
            })

    return products


if __name__ == "__main__":

    url = "https://www.brickmo.com/en/lego/lego-icons/"

    products = scrape_page(url)

    # Convert to DataFrame
    df = pd.DataFrame(products)

    # Save CSV in the current folder
    df.to_csv(
        "brickmo_prices.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n{len(products)} products saved to brickmo_prices.csv")