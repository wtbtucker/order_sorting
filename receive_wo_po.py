import pandas as pd
import os

# set path to current file location
path = os.path.dirname(os.path.realpath(__file__))

# direct to the orders file itself and open it
orders_path = path + "\\orders.csv"

# csv or txt for output file
scan_path = path + "\\scan_upload.csv"

with open(orders_path, "r") as o:
    orders = pd.read_csv(o, dtype = {"Product barcode":str, "Line item quantity":int})

# check datatype of orders
orders_dtype = orders.dtypes
print(orders_dtype)

# initialize empty list to add barcodes
barcode_list = []

for index, row in orders.iterrows():
    if not row("Note") == 99:

