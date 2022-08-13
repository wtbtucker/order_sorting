import os
import csv

# set path to current file location
path = os.path.dirname(os.path.realpath(__file__))

# direct to the orders file itself and open it
orders_path = path + "\\orders.csv"
output_path = path + "\\99 scan upload.txt"

# initialize empty list of barcodes
barcode_list = []

# open the orders file and create reader object
with open(orders_path, "r") as o:
    reader = csv.DictReader(o)

    # iterate over reader add barcodes to list
    for row in reader:
        store = row["Note"]
        barcode = row["Product barcode"]

        # convert quantity to integer if not blank
        if row["Line item quantity"]:
            quantity = int(row["Line item quantity"])
        else:
            quantity = 0
        
        # add barcode quantity times to barcode_list
        if store != "99":
            while quantity > 0:
                barcode_list.append(barcode)
                quantity = quantity - 1

# open output file with blank first line
with open(output_path, "w") as output:
    output.write("\n")
    
    # add barcode_list in the required format
    for barcode in barcode_list:
        output.write(barcode)
        output.write("\t")
        output.write("01")
        output.write("\n")

