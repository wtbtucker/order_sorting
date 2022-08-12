import pandas as pd
import os

# set path variable to the current folder
# another folder with the upc_list and stock_status

path = os.path.dirname(os.path.realpath(__file__))

upc_path = path + "\\upc_list.csv"
stock_path = path + "\\stock_status.csv"
orders_path = path + "\\orders.csv"
output_path = path + "\\orders_on_hand.csv"

with open(upc_path, "r") as upc_list:
    upc = pd.read_csv(upc_list, usecols = ["Sku", "PrimaryFeature", "Upc"], dtype={"Upc":str, "PrimaryFeature":str})
    upc["COL"] = upc["PrimaryFeature"]

with open(stock_path, "r") as stock_status:
    stock = pd.read_csv(stock_status, usecols = ["StoreCode", "SKU", "COL", "OnHand"], dtype={"COL":str})

with open(orders_path, "r") as o:
    orders = pd.read_csv(o, usecols = ["Order number", "Note", "Product barcode", "Line item quantity"], dtype={"Product barcode":str})
    orders = orders.reset_index()

output1 = pd.merge(upc, stock, how="inner", left_on=["Sku","COL"], right_on=["SKU","COL"])
output2 = pd.DataFrame()

# iterate over rows in the order file
for index, row in orders.iterrows():
    # use order number from row or last order number if blank
    if not pd.isna(row["Order number"]):
        order_number = row["Order number"]
    
    # check inventory file for barcode if not field is empty
    if pd.isna(row["Note"]):
        barcode = row["Product barcode"]
        df = output1.loc[output1["Upc"] == barcode]

        # append order number to inventory information and append
        df.insert(0, "order_number", order_number)
        frames = [df, output2]
        output2 = pd.concat(frames)

output2.to_csv(output_path, index="false", columns=["order_number", "StoreCode", "OnHand", "SKU", "COL", "Upc"])