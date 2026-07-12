## Linda - testing which LEGO shops are actually scrapable before building the real scraper
## Checking robots.txt rules + whether a real request goes through cleanly

import requests
from urllib.robotparser import RobotFileParser

url = "https://www.lego.com/de-de/product/hogwarts-castle-71043"
domain = "https://www.lego.com"

headers = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}

rp = RobotFileParser()
rp.set_url(f"{domain}/robots.txt")
rp.read()
allowed = rp.can_fetch(headers["User-Agent"], url)

response = requests.get(url, headers=headers, timeout=10)
status = response.status_code

print(f"robots.txt allows = {allowed}, real request status = {status}")