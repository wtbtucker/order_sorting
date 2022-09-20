import pandas as pd
import os
from random import randint

# TODO fix last row
# remove orders with notes and items without barcodes

def main():
    # set path for input and output files
    path = os.path.dirname(os.path.realpath(__file__))
    upc_path = path + "\\upc_list.csv"
    stock_path = path + "\\stock_status.csv"
    orders_path = path + "\\orders.csv"
    output_path = path + "\\orders_on_hand.csv"

    # open input files into pandas dataframes
    upc_df = open_upc_file(upc_path)
    stock_df = open_stock_file(stock_path)
    inventory_df = pd.merge(upc_df, stock_df, how="inner", left_on=["Sku","COL","ROW"], right_on=["SKU","COL","ROW"])
    orders = open_orders_file(orders_path)
        
    # Remove line items without barcodes and orders with notes
    orders = remove_notes(orders)
    orders = remove_team_sales(orders)
        

    # merge inventory files and initialize output dataframe
    
    output2 = pd.DataFrame(columns=["order_number", "StoreCode", "OnHand", "SKU", "COL", "Upc"])

    # iterate over rows in the order file
    count = 0
    for i in range(0, (len(orders))):
        # after multi-line order start at the next order, not the next row
        if i < count:
            continue
        row = orders.iloc[i]
        order_number = row["Order number"]
        order_length = len(orders.loc[orders["Order number"] == order_number])

        # multi-item orders
        if order_length > 1 or row["line_item_quantity"] > 1:   
            temp_df = pd.DataFrame()

            # create dataframe of queries for all items on order
            while orders.iloc[i]["Order number"] == order_number:
                line_item_code = str(orders["Product barcode"].iloc[i])
                multi_df = inventory_df.loc[inventory_df["Upc"] == line_item_code]

                # add stores with line_item_quantity on hand or ensure sort to multiple stores
                line_item_quantity = orders["line_item_quantity"].iloc[i]
                if not multi_df.loc[multi_df["OnHand"] >= line_item_quantity].empty:
                    multi_df = multi_df.loc[multi_df["OnHand"] >= line_item_quantity]
                else:
                    order_length = order_length + 1
                temp_df = pd.concat([multi_df, temp_df])
                i = i + 1
                count = i
                if i >= len(orders):
                    break

            # sort multi-line order and append to output dataframe
            sorted_multi_df = temp_df.groupby("StoreCode").filter(lambda x: len(x) == order_length)

            if not sorted_multi_df.empty:
                store = sort_multi(sorted_multi_df)
                orders["Note"].iloc[(i-order_length):(i)] = store
            else:
                temp_df = multi_store_mode(temp_df)
                temp_df.insert(0, "order_number", order_number)
                output2 = pd.concat([temp_df, output2])

        else:
            # return dataframe of inventory rows that match barcode
            barcode = row["Product barcode"]
            df = inventory_df.loc[inventory_df["Upc"] == barcode]
            
            if not df.empty:
                store = sort_single(df)
                # append order number to inventory information and add to output dataframe
                orders["Note"].iloc[i] = store

    # TODO: initialize columns for output 2
    orders.to_csv(orders_path)
    output2['order_number'] = output2['order_number'].astype(str)
    output2 = output2.sort_values(by="order_number", ascending=False)
    output2.to_csv(output_path, index="false", columns=["order_number", "StoreCode", "OnHand", "SKU", "COL", "Upc"])

def open_upc_file(upc_path):
    with open(upc_path, "r") as upc_list:
        upc = pd.read_csv(upc_list, usecols = ["Sku", "PrimaryFeature", "SecondaryFeature", "Upc"], dtype={"Upc":str, "PrimaryFeature":str, "SecondaryFeature":str})
        upc["COL"] = upc["PrimaryFeature"]
        upc["ROW"] = upc["SecondaryFeature"]
        return upc

def open_stock_file(stock_path):
    with open(stock_path, "r") as stock_status:
        stock = pd.read_csv(stock_status, usecols = ["StoreCode", "SKU", "COL", "ROW", "OnHand"], dtype={"COL":str, "ROW":str})
        removed_stores = [9, 55, 97, 98]
        stock = stock[~stock.StoreCode.isin(removed_stores)]
        return stock

def open_orders_file(orders_path):
    with open(orders_path, "r") as o:
        orders = pd.read_csv(o, usecols = ["Order number", "Note", "Product barcode", "Line item title", "Line item variant title", "Line item quantity"], dtype={"Product barcode":str})
    orders["line_item_quantity"] = orders["Line item quantity"]
    
    # add order number and note to multi-line orders
    orders = extrapolate_order_information(orders)
    return orders

def extrapolate_order_information(orders):
    for i in range(len(orders)):
        row = orders.iloc[i]
        if not pd.isna(row["Order number"]):
            order_number = row["Order number"]
            note = row["Note"]
        else:
            orders.loc[i,"Order number"] = order_number
            orders.loc[i,"Note"] = note
    return orders

def remove_notes(orders):
    orders = orders.loc[orders["Note"].isnull()]
    return orders

def remove_team_sales(orders):
    orders = orders.loc[~orders["Product barcode"].isnull()]
    return orders

def sort_multi(sorted_multi_df):
    
    # TODO add support for multi-line item quantity beyond the current stopgap
    
    # TODO maintain the order of the original orders columns
    if not sorted_multi_df.loc[sorted_multi_df.StoreCode == 99].empty:
        store = 99
    elif not sorted_multi_df.loc[sorted_multi_df.StoreCode == 8].empty:
        store = 8
    else:
        random_row = randint(1, len(sorted_multi_df)) - 1
        store = sorted_multi_df.iloc[random_row]["StoreCode"]
    return store


def sort_single(df):
    if len(df.loc[df.StoreCode == 99]) > 0:
        store = 99
    elif len(df.loc[df.StoreCode == 8]) > 0:
        store = 8
    else:
        # select random store
        df = df.sample(frac=1).reset_index(drop=True)
        store = df.loc[df.OnHand.idxmax(), "StoreCode"]
    return store


# recursion within the function until temp_df = empty
def multi_store_mode(temp_df):
    # initialize empty dataframe to concat our queries to
    multi_store_df = pd.DataFrame()

    # base case of empty temp_df
    while not temp_df.empty:
        # actual sorting function
        mode_list = temp_df["StoreCode"].mode().tolist()
        if 99 in mode_list:
            mode_store = 99
        elif 8 in mode_list:
            mode_store = 8
        else:
            mode_store = mode_list[randint(1, len(mode_list))-1]
        most_queries = temp_df.loc[temp_df.StoreCode == mode_store]
        mode_upc = most_queries.Upc.tolist()
        multi_store_df = pd.concat([multi_store_df,most_queries])
        temp_df = temp_df[~temp_df.Upc.isin(mode_upc)]
    return multi_store_df
    

main()