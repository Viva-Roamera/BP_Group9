## Linda - testing which LEGO shops are actually scrapable before building the real scraper
## Checking robots.txt rules + whether a real request goes through cleanly

import requests
from urllib.robotparser import RobotFileParser

def test_lego():
    ## Result first try: robots.txt allows = True, real request status = 403
    ## LEGO's own rules say this page is fine to scrape, but the live server is refusing the request anyway
    ## Will update headers and try rerunning to see if status code changes
    ## Original headers - blocked with 403
    # headers = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}
    ## Updated headers - added Accept-Language and Accept to look more like a real browser
    ## LEGO.com test (12 Jul 2026): robots.txt allows scraping, but server blocks non-browser requests (403) even with browser-style headers
    ## Chose not to disguise our script as a real browser to bypass this, staying transparent about being an automated tool
    ## Decision: LEGO.com excluded, moving to next candidate shop

    url = "https://www.lego.com/de-de/product/hogwarts-castle-71043"
    domain = "https://www.lego.com"

    
    headers = {
        "User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    rp = RobotFileParser()
    rp.set_url(f"{domain}/robots.txt")
    rp.read()
    allowed = rp.can_fetch(headers["User-Agent"], url)

    response = requests.get(url, headers=headers, timeout=10)
    status = response.status_code

    print(f"robots.txt allows = {allowed}, real request status = {status}")

    