"""
LEGO Price Data Visualization
-------------------------------
Reads master_product_list.csv, cleans it, builds a PriceComparison.xlsx
workbook (with live formulas), and produces two charts:
  1. Lowest Price Wins  (count of products where each shop had the lowest price)
  2. Price Range by Category (lowest -> highest price per category)
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

candidate_inputs = [
    OUTPUT_DIR / "master_product_list.csv",
    SCRIPT_DIR / "master_product_list.csv",
    Path("/mnt/user-data/uploads/master_product_list.csv"),
]
INPUT_CSV = next((path for path in candidate_inputs if path.exists()), candidate_inputs[0])

candidate_workbooks = [
    OUTPUT_DIR / "PriceComparison.xlsx",
    SCRIPT_DIR / "PriceComparison.xlsx",
    Path("/mnt/user-data/outputs/PriceComparison.xlsx"),
]
OUTPUT_XLSX = next((path for path in candidate_workbooks if path.exists()), candidate_workbooks[0])
CHART1_PATH = OUTPUT_DIR / "lowest_price_wins.png"
CHART2_PATH = OUTPUT_DIR / "price_range_by_category.png"

if not OUTPUT_XLSX.exists():
    raise FileNotFoundError(
        f"Workbook not found at {OUTPUT_XLSX}. Run PriceComparisonAnalysis.py first."
    )

# Read the already-computed (and recalculated) comparison table
wb = openpyxl.load_workbook(OUTPUT_XLSX, data_only=True)
ws = wb["PriceComparison"]
rows = list(ws.iter_rows(min_row=2, values_only=True))
cmp_df = pd.DataFrame(rows, columns=[
    "ProductID", "ProductName", "Category",
    "LowestPrice", "LowestShop", "HighestPrice", "HighestShop",
    "PriceDiff", "NumShops",
])

# Also load the cleaned Raw Data (for category-level price range across ALL
# listings, not just the min/max already summarized per product)
ws_raw = wb["Raw Data"]
raw_rows = list(ws_raw.iter_rows(min_row=2, values_only=True))
raw_df = pd.DataFrame(raw_rows, columns=["shop", "ProductID", "category", "name", "price"])

# ---------------------------------------------------------------------------
# CHART 1: Lowest Price Wins
# Only products carried by 2+ shops are meaningful for a "who's cheaper" count
# (a single-shop product trivially "wins" by default, which would just be
# noise reflecting how many products each shop happens to list).
# ---------------------------------------------------------------------------
multi_shop = cmp_df[cmp_df["NumShops"] > 1]
wins = multi_shop["LowestShop"].value_counts()

# Make sure every shop that appears anywhere in the data shows on the chart,
# even if it never won on a shared product (so it isn't silently omitted).
all_shops = sorted(raw_df["shop"].unique())
wins = wins.reindex(all_shops, fill_value=0).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 6))
colors = plt.cm.tab10.colors
bars = ax.bar(wins.index, wins.values, color=colors[:len(wins)])
for bar, val in zip(bars, wins.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            str(int(val)), ha="center", va="bottom", fontsize=11)

ax.set_title(
    f"Number of Sets Where Shop Had the Lowest Price\n"
    f"(out of {len(multi_shop)} sets sold by 2+ shops)"
)
ax.set_ylabel("Sets won (lowest price)")
ax.set_ylim(0, max(wins.values) * 1.2 if wins.values.max() > 0 else 1)
plt.tight_layout()
plt.savefig(CHART1_PATH, dpi=150)
plt.close()
print(f"Saved: {CHART1_PATH}")
print(wins)

# ---------------------------------------------------------------------------
# CHART 2: Price Range by Category
# For each category: overall lowest price and overall highest price seen
# across all shops/listings in that category.
# ---------------------------------------------------------------------------
cat_range = raw_df.groupby("category")["price"].agg(["min", "max"]).reset_index()
cat_range = cat_range.sort_values("max", ascending=True)

fig, ax = plt.subplots(figsize=(8, max(4, 0.5 * len(cat_range) + 1.5)))
y_pos = np.arange(len(cat_range))

ax.hlines(y=y_pos, xmin=cat_range["min"], xmax=cat_range["max"],
          color="lightgray", linewidth=4, zorder=1)
ax.scatter(cat_range["min"], y_pos, color="#2e7d32", s=90, zorder=2, label="Lowest price")
ax.scatter(cat_range["max"], y_pos, color="#e35d40", s=90, zorder=2, label="Highest price")

ax.set_yticks(y_pos)
ax.set_yticklabels(cat_range["category"])
ax.set_xlabel("Price (\u20ac)")
ax.set_title("Price Range by Category\n(lowest -> highest, across all shops)")
ax.legend(loc="lower right")
ax.set_xlim(left=0)
plt.tight_layout()
plt.savefig(CHART2_PATH, dpi=150)
plt.close()
print(f"Saved: {CHART2_PATH}")
print(cat_range)
