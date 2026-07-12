from data_collection import collect_data
from storage import save_to_csv


print("Starting LEGO competitor price automation...")


products = collect_data()

save_to_csv(products)


print("Automation completed.")

