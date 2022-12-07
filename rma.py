from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException 
import os
import csv

driver = webdriver.Edge()
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

def main():
    global driver
    login()
    navigate_store('1') # navigate to store 1 for the RMA menu to appear
    nagivate_rma()
    print(store_names)
    
    # navigate to each store in the list of stores
    # create a list of barcodes associated with each store
    #

    driver.quit()

def login():
    global driver
    driver.get('https://marathonsportsma.enterprise.ricssoftware.com/Login.aspx?')

    usernameElement = driver.find_element(By.ID, 'textbox_user_name')
    usernameElement.send_keys('online sales')
    passwordElement = driver.find_element(By.ID, 'textbox_pass_word')
    passwordElement.send_keys('Runner$4')
    passwordElement.send_keys(Keys.ENTER)

def navigate_store(store_number):
    global driver
    storeCode = driver.find_element(By.ID, 'ctl00_lblOrganization')
    storeInputElement = driver.find_element(By.ID, 'ctl00_otxtQuickOrganizationNavigation_txtOrganizationCriteriaEntry')
    storeInputElement.send_keys(store_number)
    storeInputElement.send_keys(Keys.RETURN)
    WebDriverWait(driver, timeout=10).until(EC.text_to_be_present_in_element((By.ID, 'ctl00_lblOrganization'), store_number))

def nagivate_rma():
    nagivate_menu('ctl00_btnStock')
    nagivate_menu('n3')
    nagivate_menu('n14')

def nagivate_menu(id):
    try:
        element = driver.find_element(By.ID, id)
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.click(element)
        actions.perform()
    except StaleElementReferenceException:
        element = driver.find_element(By.ID, id)
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.click(element)
        actions.perform()

def create_store_dict():
    global store_names

    # open the orders csv file and create reader object
    path = os.path.dirname(os.path.realpath(__file__))
    orders_path = path + "\\orders.csv"
    with open(orders_path, "r") as o:
        reader = csv.DictReader(o)

        # iterate over reader and create dictionary with stores as keys and barcodes as values
        for row in reader:
            store = row["Note"]
            barcode = row["Product barcode"]

            # convert quantity to integer if not blank
            if row["Line item quantity"]:
                quantity = int(row["Line item quantity"])
            else:
                quantity = 0

            


main()