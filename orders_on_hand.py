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
    upc = pd.read_csv(upc_list, usecols = ["Sku", "PrimaryFeature", "SecondaryFeature", "Upc"], dtype={"Upc":str, "PrimaryFeature":str, "SecondaryFeature":str})
    upc["COL"] = upc["PrimaryFeature"]
    upc["ROW"] = upc["SecondaryFeature"]
with open(stock_path, "r") as stock_status:
    stock = pd.read_csv(stock_status, usecols = ["StoreCode", "SKU", "COL", "ROW", "OnHand"], dtype={"COL":str, "ROW":str})
with open(orders_path, "r") as o:
    orders = pd.read_csv(o, usecols = ["Order number", "Note", "Product barcode", "Line item quantity"], dtype={"Product barcode":str})
    orders["line_item_quantity"] = orders["Line item quantity"]

    # add order number and note to multi-line orders
    for i in range(len(orders)):
        row = orders.iloc[i]
        if not pd.isna(row["Order number"]):
            order_number = row["Order number"]
            note = row["Note"]
        else:
            orders.loc[i,"Order number"] = order_number
            orders.loc[i,"Note"] = note
    
    # remove orders with notes
    orders = orders.loc[orders["Note"].isnull()]
    orders = orders.reset_index()

# merge inventory files and initialize output dataframe
output1 = pd.merge(upc, stock, how="inner", left_on=["Sku","COL","ROW"], right_on=["SKU","COL","ROW"])
output2 = pd.DataFrame()

# iterate over rows in the order file
count = 0
for i in range(0, (len(orders) - 1)):
    # after multi-line order start at the next order, not the next row
    if i < count:
        continue
    
    row = orders.iloc[i]
    order_number = row["Order number"]
    order_length = len(orders.loc[orders["Order number"] == order_number])

   # if multiple items associated with an order add those rows to a temporary dataframe
    if order_length > 1 or row["line_item_quantity"] > 1:   
        temp_df = pd.DataFrame()
        while orders.iloc[i]["Order number"] == order_number and i in range(0, (len(orders) - 1)):
            
            # query inventory file for stores with the line item in stock
            line_item_code = orders.loc[i, "Product barcode"]
            multi_df = output1.loc[output1["Upc"] == line_item_code]

            # add only those stores with enough OnHand to fulfill item to dataframe
            line_item_quantity = orders.loc[i, "line_item_quantity"]
            if not multi_df.loc[multi_df["OnHand"] >= line_item_quantity].empty:
                multi_df = multi_df.loc[multi_df["OnHand"] >= line_item_quantity]
            
            # ensure order not sorted to a single store
            else:
                order_length = order_length + 1
            
            # append to dataframe and move onto next row associated with order
            temp_list = [multi_df, temp_df]
            temp_df = pd.concat(temp_list)
            i = i + 1
            count = i


        # count the number of entries each store has in the temporary dataframe (succesful queries)
        sorted_multi_df = temp_df.groupby("StoreCode").filter(lambda x: len(x) == order_length)

        if not sorted_multi_df.loc[sorted_multi_df.StoreCode == 99].empty:
            temp_df = sorted_multi_df.loc[sorted_multi_df.StoreCode == 99]
        elif not sorted_multi_df.loc[sorted_multi_df.StoreCode == 8].empty:
            temp_df = sorted_multi_df.loc[sorted_multi_df.StoreCode == 8]
        elif not sorted_multi_df.empty:
            # TODO: select store with the greatest quantity on hand
            temp_df = sorted_multi_df.head(order_length)
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

            # append order number to inventory information and add to output dataframe
            df.insert(0, "order_number", order_number)  
            output2 = pd.concat([df,output2])

output2.order_number = output2.order_number.astype(str)
output2 = output2.sort_values(by="order_number", ascending=False)
output2.to_csv(output_path, index="false", columns=["order_number", "StoreCode", "OnHand", "SKU", "COL", "Upc"])
