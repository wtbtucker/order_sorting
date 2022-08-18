import csv
import os
from pyperclip import copy
from itertools import tee, islice, chain


def main():
    # set path to the orders file
    path = os.path.dirname(os.path.realpath(__file__))
    input_path = path + "\\orders.csv"

    while True:
        # open file into reader object
        with open(input_path, "r") as file:
            reader = csv.DictReader(file)
            store = user_input()
            store_number = store[1]
            store_name = store[0]

            prelim_template = "Hi " + store_name
            # create a list from the dictreader
            orders = []
            for row in reader:
                order = row
                orders.append(order)

            store_orders = generate_templates(store_number,orders)
                # if length of list is 0 return a blank template
            if len(store_orders) == 0:
                print("No orders")
            else:
                # create second half of email template
                text = ",\n\nCould you please fulfill the following orders?\n\n"
                for i in store_orders:
                    text = text + i + "\n"
                text = text + "\nMake sure to confirm SKU, size, and quantity before sealing the box. Please reply to this email to confirm.\n\nSincerely\nBill"
                # combine first half and second half of template. print and copy to clipboard
                end_template = prelim_template + text
                print(end_template)
                copy(end_template)


def generate_templates(store, order_list):
    # initialize empty list of order numbers
    store_orders = []
    

    for current in order_list:
        current_store = current["Note"]
        current_order = current["Order number"]

        # check for multi-store line items
        if "," in current_store:
            print("Please fix multi-store line item")
            # need a return value here to stop iteration

        # append current order to list only if it does not match the previous order
        # elif current_order == "":
        #     print("Please fix blank order numbers")
        elif current_store == store:
            store_orders.append(current_order)

    return store_orders


def user_input():
    # initialize dictionary of store names and numbers
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
                        Portsmouth = 17,
                        Manchester = 18,
                        Concord = 19,
                        Northampton = 20,
                        Canton = 96)
    
    # continuously prompt user for input until store number entered. quit if quit      
    while True:
        # conditional for successful conversion to int
        # store as variable
        store = input("Enter store number: ")
        if store == "quit":
            quit()
        elif int(store) in list(store_names.values()):
            store_name = list(store_names.keys())[list(store_names.values()).index(int(store))]
            store_number = store
            return store_name, store_number

def neighbor_orders(iterable):
    #iterator = iter(iterable)
    prevs, currents, nexts = tee(iterable, 3)
    prevs = chain([None],prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, currents)
main()