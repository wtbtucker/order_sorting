import pandas as pd
import os

# set path for input and output files
path = os.path.dirname(os.path.realpath(__file__))
upc_path = path + "\\upc_list.csv"
stock_path = path + "\\stock_status.csv"
orders_path = path + "\\orders.csv"
output_path = path + "\\orders_on_hand.csv"

# open input files into pandas dataframes
with open(upc_path, "r") as upc_list:
    upc = pd.read_csv(upc_list, usecols = ["Sku", "PrimaryFeature", "Upc"], dtype={"Upc":str, "PrimaryFeature":str})
    upc["COL"] = upc["PrimaryFeature"]

with open(stock_path, "r") as stock_status:
    stock = pd.read_csv(stock_status, usecols = ["StoreCode", "SKU", "COL", "OnHand"], dtype={"COL":str})

with open(orders_path, "r") as o:
    orders = pd.read_csv(o, usecols = ["Order number", "Note", "Product barcode", "Line item quantity"], dtype={"Product barcode":str})
    orders["line_item_quantity"] = orders["Line item quantity"]
    # remove orders with existing notes
    orders = orders.loc[orders["Note"].isnull()]

    # remove orders with existing notes
    # TODO: remove multi line item orders with notes
    for i in range(len(orders)):
        row = orders.iloc[i]
        if not pd.isna(row["Order number"]):
            order_number = row["Order number"]
        else:
            orders.loc[i,"Order number"] = order_number
    orders = orders.reset_index()

output1 = pd.merge(upc, stock, how="inner", left_on=["Sku","COL"], right_on=["SKU","COL"])
output2 = pd.DataFrame(index=["order_number", "StoreCode", "OnHand", "SKU", "COL", "Upc"])

# iterate over rows in the order file
count = 0
for i in range(0, (len(orders) - 1)):
    if i < count:
        continue
    
    row = orders.iloc[i]
    order_number = row["Order number"]
   
   # if multiple rows associated with an order add those rows to a temporary dataframe
    if len(orders.loc[orders["Order number"] == order_number]) > 1:   
        temp_df = pd.DataFrame()
        while orders.iloc[i]["Order number"] == order_number and i in range(0, (len(orders) - 1)):
            
            # query inventory file for stores with the line item in stock
            # TODO: line item quantity
            # line_item_quantity = orders.loc[i, "line_item_quantity"]
            line_item_code = orders.loc[i, "Product barcode"]

            multi_df = output1.loc[output1["Upc"] == line_item_code]

            # append line item quantity?
            temp_list = [multi_df, temp_df]
            temp_df = pd.concat(temp_list)
            i = i + 1
            count = i

        # total number of items on the order
        line_items = orders.loc[orders["Order number"] == order_number].line_item_quantity.agg(sum)

        # count the number of entries each store has in the temporary dataframe (succesful queries)
        sorted_multi_df = temp_df.groupby("StoreCode").filter(lambda x: len(x) >= line_items)
        if not sorted_multi_df.loc[sorted_multi_df.StoreCode == 99].empty:
            temp_df = sorted_multi_df.loc[sorted_multi_df.StoreCode == 99]
        elif not sorted_multi_df.loc[sorted_multi_df.StoreCode == 8].empty:
            temp_df = sorted_multi_df.loc[sorted_multi_df.StoreCode == 8]
        elif not sorted_multi_df.empty:
            temp_df = sorted_multi_df
        temp_df.insert(0, "order_number", order_number)
        multi_frames = [temp_df, output2]
        output2 = pd.concat(multi_frames)

    else:
        # return dataframe of inventory rows that match barcode
        barcode = row["Product barcode"]
        df = output1.loc[output1["Upc"] == barcode]
        
        if not df.empty:
            if len(df.loc[df.StoreCode == 99]) > 0:
                df = df.loc[df.StoreCode == 99]
            elif len(df.loc[df.StoreCode == 8]) > 0:
                df = (df.loc[df.StoreCode == 8])
            else:
                df = df.sample(frac=1).reset_index(drop=True)
                df = df.loc[[df.OnHand.idxmax()]]
                # print(s)
                # output2.append(s, ignore_index=True)
            # randomize then select idxmax
            # df = df.loc[df.OnHand.idxmax]
            # check for 99 then check for 8 within the dataframe

            # append order number to inventory information
            df.insert(0, "order_number", order_number)
            
            frames = [df, output2]
            output2 = pd.concat(frames)

output2.to_csv(output_path, index="false", columns=["order_number", "StoreCode", "OnHand", "SKU", "COL", "Upc"])
