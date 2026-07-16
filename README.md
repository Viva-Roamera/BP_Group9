# LEGO Competitor Price Tracker — Toy Retail Market

A Python automation that collects, stores, and compares competitor
prices across 3 online toy shops for 20 popular LEGO sets, and produces
a business report with tables and charts to support pricing decisions
and make a toy retailer's LEGO offering more competitive.

## Business area
**Toy Retailing — LEGO Sets**, spanning Star Wars, Icons,
City, Ninjago.

## Shops monitored
- Brickmo
- Zavvi
- BricksDirect
- JP Spielwaren

## Project structure
```
lego_price_tracker/
├── WebScraping             # 4 shops with LEGO in the offerings
│   ├── WebScraping2.py     # scraping prices from Zavvi
│   ├── WebScraping3.py     # scraping prices from BricksDirect
│   ├── WebScraping4.py     # scraping prices from Brickmo
│   ├── WebScraping5.py     # scraping prices from JP Spielwaren
│   └── WebScraping6.py     # scraping prices from Brickmo with extended products + category
├── DataCleansing.py        # cleanse and normalize raw data, create ProductID into staging files
├── PriceComparison.py      # price comparison: lowest/highest price, gaps --> extract excel output
├── DataVisualization.py    # create matplotlib charts 
├── staging                 # store staging files from DataCleansing.py
└── outputs
    ├── master_product_list.csv             # consolidated price from all shops
    ├── price_comparison_report.xlsx
    ├── chart_avg_price_by_shop.png
    ├── chart_price_range_by_product.png
    ├── lowest_price_wins.png               # chart 1
    ├── price_range_by_category.png         # chart 2
    └── LEGO_Price_Report.docx              # final business report (to be uploaded from OneDrive)
```

## How to run
```bash
python3 main.py                 # collect data, analyze, build charts
node report/build_report.js     # build the final Word report
```

## Data collected per observation
`product_id, name, category, shop, url, price`

Product names include the official LEGO set number (e.g. "LEGO Star Wars
Millennium Falcon (75192)") — used purely as a factual product
identifier, the same way any price-comparison site lists products.

## Data sources & ethics
This project follows a responsible data-collection pattern:
- **No personal data** is collected — only public product/price info.
- **Rate limiting**: a randomized delay is applied between every request.
- **Transparent identity**: a descriptive `User-Agent` string is used so a
  real shop could identify (and, if desired, block) the bot.
- **robots.txt respected**: checks robots.txt before any
  live request and skips pages that disallow scraping.
- **No copyrighted material reproduced**: only set names/numbers and
  prices are collected — no LEGO box art, images, or descriptive copy.

**Trademark note:** LEGO® is a trademark of the LEGO Group. This is an
independent, unofficial market-research tool, not affiliated with,
sponsored by, or endorsed by the LEGO Group.

## Output
- **CSV** — portable raw data exports
- **Excel** (`price_comparison_report.xlsx`) — Raw Data, Price Comparison sheets
- **Word report** (`LEGO_Price_Report.docx`) — Project title; Group members; Selected option; Business problem; Solution developed; Main features; Technologies or tools used; Screenshots; Testing evidence;
Limitations and future improvements; AI-use statement, if AI tools were used.
