import requests
from bs4 import BeautifulSoup
import time


def get_product_price(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9"
    }

    session = requests.Session()

    try:
        print("Waiting before request...")
        time.sleep(5)

        response = session.get(
            url,
            headers=headers,
            timeout=30
        )

        print("Status code:", response.status_code)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        price_element = soup.find(
            "span",
            class_="price"
        )

        if price_element:
            return price_element.get_text(strip=True)

        return "Price not found"

    except requests.exceptions.RequestException as error:
        return f"Request error: {error}"


url = "https://www.jb-spielwaren.de/eiffel-tower-privater-sammlungsverkauf-im-namen-vom-eigentuemer/a-648671078/"

price = get_product_price(url)

print("Product price:", price)