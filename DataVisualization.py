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

# Load the workbook and read the Raw Data sheet, which contains the actual
# price listings used for the comparison and charts.
wb = openpyxl.load_workbook(OUTPUT_XLSX, data_only=True)
ws_raw = wb["Raw Data"]
raw_rows = list(ws_raw.iter_rows(min_row=2, values_only=True))
raw_df = pd.DataFrame(raw_rows, columns=["shop", "ProductID", "category", "name", "price"])

# Clean and normalize the raw data so the charts can be computed reliably.
raw_df["price"] = pd.to_numeric(raw_df["price"], errors="coerce")
raw_df = raw_df.dropna(subset=["price"]).copy()
raw_df["shop"] = raw_df["shop"].astype(str).str.strip()
raw_df["ProductID"] = pd.to_numeric(raw_df["ProductID"], errors="coerce")
raw_df = raw_df.dropna(subset=["ProductID"]).copy()
raw_df["ProductID"] = raw_df["ProductID"].astype(int)

# ---------------------------------------------------------------------------
# CHART 1: Lowest Price Wins
# Count products where each shop offered the lowest price among the shops
# that listed that product. Only products carried by 2+ shops are included.
# ---------------------------------------------------------------------------
shared_products = raw_df.groupby("ProductID").filter(lambda g: g["shop"].nunique() > 1)

if shared_products.empty:
    wins = pd.Series(0, index=sorted(raw_df["shop"].unique()), dtype=int)
else:
    winner_per_product = (
        shared_products.sort_values(["ProductID", "price"])
        .groupby("ProductID", as_index=False)
        .first()
    )
    wins = winner_per_product["shop"].value_counts()
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
    f"(out of {shared_products['ProductID'].nunique()} sets sold by 2+ shops)"
)
ax.set_ylabel("Sets won (lowest price)")
ax.set_ylim(0, max(wins.values) * 1.2 if len(wins) and wins.values.max() > 0 else 1)
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

# ==========================================================
# CHART 3
# Price comparison for products available in 2+ shops
# ==========================================================

# Pivot on ProductID ONLY — name text can differ slightly between shops
comparison = (
    raw_df.pivot_table(
        index="ProductID",
        columns="shop",
        values="price",
        aggfunc="min"
    )
    .reset_index()
)

# Attach one representative name per ProductID (first non-null name seen)
name_lookup = (
    raw_df.dropna(subset=["name"])
    .drop_duplicates(subset=["ProductID"])
    .set_index("ProductID")["name"]
)
comparison["name"] = comparison["ProductID"].map(name_lookup)

shop_columns = [c for c in comparison.columns if c not in {"ProductID", "name"}]

comparison["ShopCount"] = comparison[shop_columns].notna().sum(axis=1)
comparison_2shops = comparison[comparison["ShopCount"] >= 2].copy()

if comparison_2shops.empty:
    print("No products with data in 2+ shops — skipping Chart 3.")
    CHART3_PATH = None
else:
    comparison_2shops["PriceGap"] = (
        comparison_2shops[shop_columns].max(axis=1)
        - comparison_2shops[shop_columns].min(axis=1)
    )
    comparison_2shops["Cheapest Shop"] = comparison_2shops[shop_columns].idxmin(axis=1)
    comparison_2shops["Most Expensive Shop"] = comparison_2shops[shop_columns].idxmax(axis=1)

    chart3_data = comparison_2shops.nlargest(20, "PriceGap").copy()
    chart3_data = chart3_data.set_index("name")

    fig, ax = plt.subplots(figsize=(18, 8))
    chart3_data[shop_columns].plot(kind="bar", ax=ax, width=0.8)
    ax.set_title("Top 20 Products by Price Gap (Available in 2+ Shops)")
    ax.set_xlabel("Product")
    ax.set_ylabel("Price (€)")
    ax.legend(title="Shop", bbox_to_anchor=(1.02, 1))
    plt.tight_layout()

    CHART3_PATH = OUTPUT_DIR / "price_comparison_2plus_shops.png"
    plt.savefig(CHART3_PATH, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {CHART3_PATH}")

    TABLE_PATH = OUTPUT_DIR / "price_comparison_2plus_shops.xlsx"
    chart3_data[shop_columns + ["ShopCount", "PriceGap", "Cheapest Shop", "Most Expensive Shop"]].to_excel(TABLE_PATH)
    print(f"Saved table: {TABLE_PATH}")