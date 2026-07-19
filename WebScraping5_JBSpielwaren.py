"""
## Iva - JB Spielwaren - product price scraper
Output: jb_spielwaren_prices.csv
Note: Need to install the following packages if not already installed:
    pip install pandas beautifulsoup4 selenium
============================================
"""
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
from datetime import datetime

def extract_category(url, soup):
    breadcrumb = soup.select_one('span.breadcrumb--title, span[itemprop="name"]')
    if breadcrumb:
        text = breadcrumb.get_text(" ", strip=True)
        if text:
            return text

    path_parts = [part for part in urlparse(url).path.split("/") if part]
    ignored_parts = {"en", "de", "fr", "nl", "it", "es", "pl", "cs", "hu", "uk", "ru", "lego"}
    for part in reversed(path_parts):
        if part.lower() not in ignored_parts:
            return part.replace("-", " ").replace("_", " ").title()

    return ""


def scrape_jb_spielwaren(url):

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(), options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.thumb-title.small, a.thumb-title"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        products = []

        category = extract_category(url, soup)

        for title_tag in soup.select("a.thumb-title.small, a.thumb-title, a[class*=\"thumb-title\"]"):
            parent = title_tag.find_parent(["div", "li", "article"])
            price_tag = None

            if parent:
                price_tag = parent.select_one("div.price, span.price")

            if not price_tag:
                price_tag = title_tag.find_next("div", class_="price")

            if not price_tag:
                price_tag = title_tag.find_next("span", class_="price")

            if title_tag and price_tag:
                name = title_tag.get_text(" ", strip=True)
                price_text = price_tag.get_text(" ", strip=True)
                price_text = (
                    price_text.replace("€", "")
                    .replace("*", "")
                    .replace(",", ".")
                    .strip()
                )

                href = title_tag.get("href", "")
                if href and not href.startswith("http"):
                    href = "https://www.jb-spielwaren.de" + href

                products.append({
                    "shop": "JB Spielwaren",
                    "category": category,
                    "name": name,
                    "price": price_text,
                    "url": href,
                    "collection_date": datetime.now().strftime("%Y-%m-%d"),
                })

        return pd.DataFrame(products)
    finally:
        driver.quit()


if __name__ == "__main__":
    START_URLS = [
        "https://www.jb-spielwaren.de/en/lego-star-wars/",
        "https://www.jb-spielwaren.de/en/lego-friends/",
        "https://www.jb-spielwaren.de/en/lego-icons/",
        "https://www.jb-spielwaren.de/en/lego-city/"
    ]

    all_products = []
    for url in START_URLS:
        df = scrape_jb_spielwaren(url)
        all_products.append(df)

    combined_df = pd.concat(all_products, ignore_index=True) if all_products else pd.DataFrame()

    if not combined_df.empty:
        combined_df.to_csv("jb_spielwaren_prices.csv", index=False, encoding="utf-8-sig")
        print(f"Saved {len(combined_df)} products")
    else:
        print("No products found")