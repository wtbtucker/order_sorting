import csv
import os
import pandas as pd
from pyperclip import copy

# user interface with button for each store
# copy email template to clipboard
# initialize Dictionary with the store names

def main():
    # set path to the orders file
    path = os.path.dirname(os.path.realpath(__file__))
    input_path = path + "\\orders.csv"

    # initialize store number and dictionary of store names
    store = 18
    store_names = dict(Norwell = 1,
                        Boston = 2,
                        Wellesley = 3,
                        Brookline = 4,
                        Cambridge = 5,
                        Melrose = 6,
                        Mansfield = 7,
                        Branford = 10,
                        Old_Saybrook = 11,
                        Plymouth = 12,
                        Yarmouth = 13,
                        Shrewsbury = 14,
                        Glastonbury = 15,
                        Fairfield = 16,
                        Manchester = 18,
                        Concord = 19,
                        Northampton = 20,
                        Canton = 96)

    # create an initial template with the store name                    
    store_name = list(store_names.keys())[list(store_names.values()).index(store)]
    prelim_template = "Hi " + store_name

    # open file into order_list
    with open(input_path, "r") as input:
        reader = csv.DictReader(input)
        orders_template = generate_templates(store,reader)
        end_template = prelim_template + orders_template
        print(end_template)
        copy(end_template)



def generate_templates(store, order_list):
    store_orders = []
    for order in order_list:
        store = str(store)
        store_number = order["Note"]
        order_number = order["Order number"]
        if store_number == store:
            store_orders.append(order_number)
    text = ",\n\nCould you please fulfill the following orders?\n\n"
    for i in store_orders:
        text = text + i + "\n"
    text = text + "\nMake sure to confirm SKU, size, and quantity before sealing the box. Please reply to this email to confirm.\n\nSincerely\nBill"
    print(text)
    return text

main()