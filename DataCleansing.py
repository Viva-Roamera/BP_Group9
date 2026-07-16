"""
## Iva - Data Cleansing for LEGO Price Comparison Analysis
1. Reads raw product price CSVs from multiple shops (Brickmo, BricksDirect, Zavvi, JB Spielwaren)
2. Cleans and standardizes the data (extracts ProductID, ensures consistent columns)
3. Saves cleaned staging CSVs in the 'staging' folder
4. Combines all cleaned data into a master product list CSV in the 'output' folder
-------------------------------
"""

import pandas as pd
import re
import os

# 1. Setup paths
staging_dir = 'staging'
output_dir = 'output'

# Ensure directories exist
for folder in [staging_dir, output_dir]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# 2. Load the data
df_brickmo2 = pd.read_csv('brickmo2_prices.csv')
df_bricksdirect = pd.read_csv('bricksdirect_prices.csv')
df_zavvi = pd.read_csv('zavvi_prices.csv', sep=';')
df_jb_spielwaren = pd.read_csv('jb_spielwaren_prices.csv')

# 3. Define extraction logic
def extract_product_id(name):
    match = re.search(r'(\d{4,8})', str(name))
    return match.group(1) if match else None

# 4. Process each dataframe
def process_file(df, shop_name):
    if 'ProductID' not in df.columns:
        df['ProductID'] = df['name'].apply(extract_product_id)
    
    if 'shop' not in df.columns:
        df['shop'] = shop_name
        
    final_cols = ['shop', 'ProductID', 'name', 'category', 'price', 'url']
    for col in final_cols:
        if col not in df.columns:
            df[col] = None
            
    return df[final_cols]

# 5. Generate staging dataframes
stg_brickmo2 = process_file(df_brickmo2, 'brickmo2')
stg_bricksdirect = process_file(df_bricksdirect, 'bricksdirect')
stg_zavvi = process_file(df_zavvi, 'zavvi')
stg_jb_spielwaren = process_file(df_jb_spielwaren, 'jb_spielwaren')
# 6. Export staging files to the 'staging' folder
stg_brickmo2.to_csv(os.path.join(staging_dir, 'stg_brickmo2_prices.csv'), index=False)
stg_bricksdirect.to_csv(os.path.join(staging_dir, 'stg_bricksdirect_prices.csv'), index=False)
stg_zavvi.to_csv(os.path.join(staging_dir, 'stg_zavvi_prices.csv'), index=False)
stg_jb_spielwaren.to_csv(os.path.join(staging_dir, 'stg_jb_spielwaren_prices.csv'), index=False)    
print(f"Staging files created successfully in the '{staging_dir}' folder.")

# 7. Create master list by reading from the staging folder
staging_files = [
    os.path.join(staging_dir, 'stg_brickmo2_prices.csv'),
    os.path.join(staging_dir, 'stg_bricksdirect_prices.csv'),
    os.path.join(staging_dir, 'stg_zavvi_prices.csv'),
    os.path.join(staging_dir, 'stg_jb_spielwaren_prices.csv')
]

df_list = [pd.read_csv(file) for file in staging_files]
master_df = pd.concat(df_list, ignore_index=True)

# 8. Save master file to the 'output' folder
master_output_path = os.path.join(output_dir, 'master_product_list.csv')
master_df.to_csv(master_output_path, index=False)

print(f"Successfully created master_product_list.csv with {len(master_df)} entries in the '{output_dir}' folder.")