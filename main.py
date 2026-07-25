"""Run the complete LEGO price-comparison pipeline.

Execution order:
1. Run the production web scrapers.
2. Clean and combine the generated CSV files.
3. Build the Excel price-comparison workbook.
4. Create the data visualisations.

Run from the project folder with:
    python main.py
"""

from pathlib import Path
import subprocess
import sys
import time


PROJECT_DIR = Path(__file__).resolve().parent

# WebScraping4.py is not included because WebScraping6_Brickmo2.py is the
# expanded Brickmo scraper used by DataCleansing.py. WebScraping1.py is also
# excluded because its output is not currently read by DataCleansing.py.
PIPELINE = [
    ("Zavvi scraper", "WebScraping2.py"),
    ("BricksDirect scraper", "WebScraping3_BricksDirect.py"),
    ("JB Spielwaren scraper", "WebScraping5_JBSpielwaren.py"),
    ("Brickmo scraper", "WebScraping6_Brickmo2.py"),
    ("Data cleansing and combination", "DataCleansing.py"),
    ("Price comparison workbook", "PriceComparison.py"),
    ("Data visualisation", "DataVisualization.py"),
]


def run_script(description: str, filename: str) -> None:
    """Run one pipeline script and stop if it fails."""
    script_path = PROJECT_DIR / filename

    if not script_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {script_path}\n"
            "Check that main.py is saved in the BP_GROUP9 project folder."
        )

    print("\n" + "=" * 70)
    print(f"STARTING: {description}")
    print(f"FILE:     {filename}")
    print("=" * 70)

    start_time = time.perf_counter()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_DIR,
        check=False,
    )

    elapsed = time.perf_counter() - start_time

    if result.returncode != 0:
        raise RuntimeError(
            f"{filename} failed with exit code {result.returncode}. "
            "The remaining pipeline steps were not run."
        )

    print(f"COMPLETED: {description} ({elapsed:.1f} seconds)")


def main() -> None:
    """Run every stage of the LEGO price-comparison project."""
    print("=" * 70)
    print("LEGO PRICE COMPARISON PIPELINE")
    print(f"Project folder: {PROJECT_DIR}")
    print("=" * 70)

    pipeline_start = time.perf_counter()

    try:
        for description, filename in PIPELINE:
            run_script(description, filename)
    except (FileNotFoundError, RuntimeError) as error:
        print("\n" + "!" * 70)
        print("PIPELINE STOPPED")
        print(error)
        print("!" * 70)
        sys.exit(1)

    total_time = time.perf_counter() - pipeline_start

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Total running time: {total_time:.1f} seconds")
    print(f"Master CSV:         {PROJECT_DIR / 'output' / 'master_product_list.csv'}")
    print(f"Excel workbook:     {PROJECT_DIR / 'output' / 'PriceComparison.xlsx'}")
    print(f"Charts folder:      {PROJECT_DIR / 'output'}")
    print("=" * 70)


if __name__ == "__main__":
    main()