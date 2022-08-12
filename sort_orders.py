import csv
import os

# set path to current file location
path = os.path.dirname(os.path.realpath(__file__))

# initialize paths to input and output files
input_path = path + "\\orders_on_hand.csv"
output_path = path + "\\sorted_orders.csv"

# open the input file
# initialize empty list variable
temporary_list = []
with open(input_path, "r") as input:
    reader = csv.DictReader(input)


# select for order number and UPC
# eventually probably want sql for this
# need to debug to see if this works

    for row in reader:
        order_number = int(row["order_number"])
        while int(row["order_number"]) == order_number:
            temporary_list.append(row)
            next row
            
            # add all entries in the list while barcode is still the same
            if row["order_number"] ==
