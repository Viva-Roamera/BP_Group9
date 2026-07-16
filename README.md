# LEGO Competitor Price Tracker — Toy Retail Market

A Python automation that collects, stores, and compares competitor
prices across 3 online toy shops for minimum 20 popular LEGO products, and produces
a business report with tables and charts to support pricing decisions
and make a toy retailer's LEGO offering more competitive.

## Business area
**Toy Retailing — LEGO Sets**, spanning Star Wars, Icons,
City, Ninjago.

## Shops monitored
- Brickmo
- Zavvi
- BricksDirect
- JB Spielwaren

## Project structure
```
lego_price_tracker/BP_GROUP9
├── main.py                 # runs the full pipeline end-to-end
├── WebScraping             # 4 shops with LEGO in the offerings
│   ├── WebScraping2.py     # scraping prices from Zavvi
│   ├── WebScraping3.py     # scraping prices from BricksDirect
│   ├── WebScraping4.py     # scraping prices from Brickmo
│   ├── WebScraping5.py     # scraping prices from JB Spielwaren
│   └── WebScraping6.py     # scraping prices from Brickmo with extended products + category
├── DataCleansing.py        # cleanse and normalize raw data, create ProductID into staging files
├── PriceComparison.py      # price comparison: lowest/highest price, gaps --> extract excel output
├── DataVisualization.py    # create matplotlib charts 
├── staging                 # store staging files from DataCleansing.py
└── outputs
    ├── master_product_list.csv             # consolidated price from all shops
    ├── price_comparison_report.xlsx        # price comparison between shops in excel format
    ├── lowest_price_wins.png               # chart 1
    ├── price_range_by_category.png         # chart 2
    └── LEGO_Price_Report.docx              # final business report (to be uploaded from OneDrive)
```

## How to run
```bash
python3 main.py                 # collect price data, cleanse, analyze, build charts

```

## Data collected per observation
`product_id, name, category, shop, url, price`

Product names include the official LEGO set number (e.g. "LEGO Star Wars
Millennium Falcon (75192)") — used purely as a factual product
identifier, the same way any price-comparison site lists products.

## Data sources & ethics
This project follows a responsible data-collection pattern:
- **No personal data** is collected — only public product/price info.
- **Rate limiting**: a delay is applied between every request.
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
- **Word report** (`LEGO_Price_Report.docx`) — Project title; Group members; Selected option; Business problem; Solution developed; Main features; Technologies or tools used; Screenshots; Testing evidence; Limitations and future improvements; AI-use statement, if AI tools were used.
