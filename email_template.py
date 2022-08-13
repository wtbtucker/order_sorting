import csv
import os
from pyperclip import copy



def main():
    # set path to the orders file
    path = os.path.dirname(os.path.realpath(__file__))
    input_path = path + "\\orders.csv"

    while True:
        store = user_input()
        store_number = store[1]
        store_name = store[0]

        prelim_template = "Hi " + store_name

        # open file into reader object
        with open(input_path, "r") as file:
            orders = csv.DictReader(file)
            orders_template = generate_templates(store_number,orders)
            if not orders_template:
                print("No orders")
            else:
                # combine first half and second half of template. print and copy to clipboard
                end_template = prelim_template + orders_template
                print(end_template)
                copy(end_template)



def generate_templates(store, order_list):
    # initialize empty list of order numbers
    store_orders = []
    
    # iterate over reader object, add order number to list if store matches store_number
    for order in order_list:
        store_number = order["Note"]
        order_number = order["Order number"]
        if store_number == store:
            store_orders.append(order_number)

    # if length of list is 0 return a blank template
    if len(store_orders) == 0:
        return None
    else:
        # create second half of email template
        text = ",\n\nCould you please fulfill the following orders?\n\n"
        for i in store_orders:
            text = text + i + "\n"
        text = text + "\nMake sure to confirm SKU, size, and quantity before sealing the box. Please reply to this email to confirm.\n\nSincerely\nBill"
        return text

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
                        Manchester = 18,
                        Concord = 19,
                        Northampton = 20,
                        Canton = 96)
    
    # continuously prompt user for input until store number entered. quit if quit      
    while True:
        store = input("Enter store number: ")   
        if store == "quit":
            quit()
        elif int(store) in list(store_names.values()):
            store_name = list(store_names.keys())[list(store_names.values()).index(int(store))]
            store_number = store
            return store_name, store_number

main()