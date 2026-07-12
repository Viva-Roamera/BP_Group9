import os


def save_to_csv(dataframe):

    os.makedirs("data", exist_ok=True)

    file_path = "data/prices.csv"

    dataframe.to_csv(
        file_path,
        index=False,
        encoding="utf-8"
    )

    print("Saved:", file_path)