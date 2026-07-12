## Linda - testing which LEGO shops are actually scrapable before building the real scraper
## Checking robots.txt rules + whether a real request goes through cleanly

import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup

def test_lego():
    ## Testing shop 1: LEGO.com
    ## Result first try: robots.txt allows = True, real request status = 403
    ## LEGO's own rules say this page is fine to scrape, but the live server is refusing the request anyway
    ## Will update headers and try rerunning to see if status code changes
    # Original header: headers = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}
    ## Updated headers - added Accept-Language and Accept to look more like a real browser
    ## Result second try: robots.txt allows = True, real request status = 403
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


def test_coolblue():
    ## Testing shop 2: Coolblue
    ## Result first try: robots.txt allows = False, real request status = 200
    ## Coolblue's own rules say don't scrape this page, but technically, the request succeeded, the page loaded just fine
    ## Will try a specific product page instead of category page to see if they are under different rules
    # Original URL: url = "https://www.coolblue.de/en/lego/lego-technic"
    ## Result second try: robots.txt allows = False, real request status = 200
    ## Decision: coolblue.de excluded, moving to next candidate shop
    
    url = "https://www.coolblue.de/en/product/972613/lego-speed-champions-aston-martin-aramco-f1-amr24-race-car-77245.html"
    domain = "https://www.coolblue.de"
    headers = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}

    rp = RobotFileParser()
    rp.set_url(f"{domain}/robots.txt")
    rp.read()
    allowed = rp.can_fetch(headers["User-Agent"], url)

    response = requests.get(url, headers=headers, timeout=10)
    print(f"Coolblue: robots.txt allows = {allowed}, real request status = {response.status_code}")

# test_coolblue()

def test_zavvi():
    ## Testing shop 3: Zavvi
    ## Result first try: robots.txt allows = True, real request status = 200
    ## Decision: Zavvi confirmed scrapable
    ## Added comments to explain each step
    ## Result second step: robots.txt allows = False, real request status = 200 Product: LEGO MINDSTORMS: EV3 Robot Coding Robotics Kit (31313) Price: Â£249.99
    ## Will inspect issues with encoding mismatch and robots.txt allows = False
    ## Debugging result: Direct robots.txt fetch status: 200 Zavvi: robots.txt allows = True, real request status = 200 Product: LEGO MINDSTORMS: EV3 Robot Coding Robotics Kit (31313) Price: £249.99
    ## Debugging resolved: RobotFileParser's own robots.txt fetch was unreliable, Fixed by fetching robots.txt myself and feeding it directly into the parser
    ## Decision: Zavvi confirmed scrapable, name and price extraction working correctly

    ## First step
    url = "https://www.zavvi.com/p/toys-lego/lego-mindstorms-ev3-robot-coding-robotics-kit-31313/10757770/"
    domain = "https://www.zavvi.com"
    headers = {"User-Agent": "Mozilla/5.0 (Group9 student project; contact: https://github.com/Viva-Roamera/BP_Group9)"}

    ## First step: Check robots.txt permission first
    rp = RobotFileParser()
    rp.set_url(f"{domain}/robots.txt")
    ## Removed rp. read() 

    ## Diagnostic: check if robots.txt itself was actually fetched successfully
    ## Will try and fetch robots.txt myself instead of letting RobotFileParser fetch it seperately
    robots_response = requests.get(f"{domain}/robots.txt", headers=headers, timeout=10)
    print(f"Direct robots.txt fetch status: {robots_response.status_code}")
    ## Removed: print(f"First 200 characters of robots.txt: {robots_response.text[:200]}")

    ## Feed the robots.txt content we already fetched directly into the parser
    rp.parse(robots_response.text.splitlines())
    allowed = rp.can_fetch(headers["User-Agent"], url)

    ## First step: Fetch the actual page
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = "utf-8" ## Fix: force correct character encoding so £ displays properly
    print(f"Zavvi: robots.txt allows = {allowed}, real request status = {response.status_code}")

    ## Second step: Parse the HTML so we can pull out real data
    soup = BeautifulSoup(response.text, "html.parser")

    ## Second step: Extract product name using its data-testid (stable identifier, less likely to break if Zavvi redesigns the site)
    name = soup.find("h1", attrs={"data-testid": "pdp-product-title"}).text.strip()

    ## Second step: Extract price using its class name
    price = soup.find("span", class_="pdp-price-text").text.strip()

    ## Second step:
    print(f"Product: {name}")
    print(f"Price: {price}")

## Only calling this test and not all
test_zavvi()