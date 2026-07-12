import pandas as pd

# Load the dataset
df = pd.read_csv("data/raw/lego_data.csv")

# Show the first 5 rows
print("FIRST 5 ROWS:")
print(df.head())

print("\n" + "=" * 50)

# Show the column names
print("COLUMN NAMES:")
print(df.columns.tolist())

print("\n" + "=" * 50)

# Show information about the dataset
print("DATASET INFORMATION:")
print(df.info())