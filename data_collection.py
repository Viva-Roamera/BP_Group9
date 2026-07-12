import pandas as pd
from datetime import date


def collect_data():

    file = "data/public_lego_prices.csv"

    df = pd.read_csv(file)

    df["collection_date"] = str(date.today())

    return df


if __name__ == "__main__":

    data = collect_data()

    print(data)