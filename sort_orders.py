import csv
import os

# set path to current file location
path = os.path.dirname(os.path.realpath(__file__))

# initialize paths to input and output files
input_path = path + "\\orders_on_hand.csv"
output_path = path + "\\sorted_orders.csv"


# initialize empty list variables
temporary_list = []
sorted_list = []

# open the input file and convert to list
with open(input_path, "r") as file:
    input = csv.DictReader(file)
    reader = list(input)
    length = len(reader)
    
    # iterate over rows in input file
    # helper functions for actually sorting the thing
    for i in range(length):
        current_row = reader[i]
        previous_row = reader[i-1]
        if current_row["order_number"] != previous_row["order_number"] and current_row["Upc"] != previous_row["Upc"]:
            print(temporary_list)
            for entry in temporary_list:
                if int(entry["StoreCode"]) == 99:
                    sorted_list.append(entry)
                    temporary_list = []
                elif int(entry["StoreCode"]) == 8:
                    sorted_list.append(entry)
                    temporary_list = []
            temporary_list = []
            temporary_list.append(current_row)
        else:
            temporary_list.append(current_row)