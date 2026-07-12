import pandas as pd


def analyze_prices():

    file_path = "data/prices.csv"

    df = pd.read_csv(file_path)

    df["price"] = pd.to_numeric(df["price"])

    results = []

    for product in df["product_name"].unique():

        product_data = df[
            df["product_name"] == product
        ]

        lowest = product_data.loc[
            product_data["price"].idxmin()
        ]

        highest = product_data.loc[
            product_data["price"].idxmax()
        ]

        difference = (
            highest["price"] -
            lowest["price"]
        )

        average = product_data["price"].mean()


        results.append(
            {
                "product_name": product,
                "lowest_shop": lowest["shop"],
                "lowest_price": lowest["price"],
                "highest_shop": highest["shop"],
                "highest_price": highest["price"],
                "price_difference": round(difference, 2),
                "average_price": round(average, 2)
            }
        )


    result_df = pd.DataFrame(results)

    return result_df



if __name__ == "__main__":

    analysis = analyze_prices()

    print(analysis)
    