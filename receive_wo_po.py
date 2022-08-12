import pandas as pd
import os
import csv

# set path to current file location
path = os.path.dirname(os.path.realpath(__file__))

# direct to the orders file itself and open it
orders_path = path + "\\orders.csv"
output_path = path + "\\99 scan upload.txt"

# csv or txt for output file
scan_path = path + "\\scan_upload.csv"

# initialize empty list to add barcodes
barcode_list = []

# open the orders file and create reader object
with open(orders_path, "r") as o:
    reader = csv.DictReader(o)

    # iterate over the rows in file adding barcode quantity times
    for row in reader:
        store = row["Note"]
        if row["Line item quantity"]:
            quantity = int(row["Line item quantity"])
        else:
            quantity = 0
        barcode = row["Product barcode"]
        if store != 99:
            while quantity > 0:
                barcode_list.append(barcode)
                quantity = quantity - 1

# write barcodes to scan_upload file
# blank first row
# barcode tab 01 newline
# add a 01 in between each actual barcode?

with open(output_path, "w") as output:
    output.write("\n")
    for barcode in barcode_list:
        output.write(barcode)
        output.write("\t")
        output.write("01")
        output.write("\n")

