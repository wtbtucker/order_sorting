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
store_names  = dict(Norwell = 1,
                        Boston = 2,
                        Wellesley = 3,
                        Brookline = 4,
                        Cambridge = 5,
                        Melrose = 6,
                        Mansfield = 7,
                        Warehouse = 8,
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
                        Canton = 96,
                        OnlineSales = 99)

def main():
    global driver
    login()
    navigate_store('1') # navigate to store 1 for the RMA menu to appear
    navigate_rma()
    store_dict = create_store_dict()
    for store in store_dict:
        navigate_store(store)
        navigate_menu('ctl00_ContentPlaceHolder1_btnScanView')
        for line_item in store_dict[store]:
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtRmaNumber').clear()
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtRmaNumber').send_keys(line_item[0])
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_productEntryList_txtIdentifier').send_keys(line_item[1])
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_productEntryList_txtIdentifier').send_keys(Keys.RETURN)
            navigate_menu('ctl00_cmdMaster5')
    driver.quit()

# Log into the RICS marathon sports store using hard-coded credentials
def login():
    global driver
    driver.get('https://marathonsportsma.enterprise.ricssoftware.com/Login.aspx?')
    usernameElement = driver.find_element(By.ID, 'textbox_user_name')
    usernameElement.send_keys('online sales')
    passwordElement = driver.find_element(By.ID, 'textbox_pass_word')
    passwordElement.send_keys('Runner$4')
    passwordElement.send_keys(Keys.ENTER)

# Type store number into the store code field
def navigate_store(store_number):
    global driver
    storeCode = driver.find_element(By.ID, 'ctl00_lblOrganization')
    storeInputElement = driver.find_element(By.ID, 'ctl00_otxtQuickOrganizationNavigation_txtOrganizationCriteriaEntry')
    storeInputElement.send_keys(store_number)
    storeInputElement.send_keys(Keys.RETURN)

    # Wait until page loads with the correct store number at top
    WebDriverWait(driver, timeout=10).until(EC.text_to_be_present_in_element((By.ID, 'ctl00_lblOrganization'), store_number))

# Select 'inventory', 'stock maintenance', then 'Enter Returns to Supplier (RMA)'
def navigate_rma():
    navigate_menu('ctl00_btnStock')
    navigate_menu('n3')
    navigate_menu('n14')

# Move to and click on HTML element
def navigate_menu(id):
    try:
        element = driver.find_element(By.ID, id)
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.click(element)
        actions.perform()
    
    # Handle stale reference errors when the page reloads
    except StaleElementReferenceException:
        element = driver.find_element(By.ID, id)
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.click(element)
        actions.perform()

def create_store_dict():
    # initialize dictionary
    store_dict = {}

    # open the orders csv file and create reader object
    path = os.path.dirname(os.path.realpath(__file__))
    orders_path = path + "\\orders.csv"
    with open(orders_path, "r") as o:
        reader = csv.DictReader(o)

        # iterate over reader and create dictionary with stores as keys and barcodes as values
        for row in reader:
            store = row["Note"]
            barcode = row["Product barcode"]
            order_number = row["Order number"]

            # convert quantity to integer if not blank
            if row["Line item quantity"]:
                quantity = int(row["Line item quantity"])
            else:
                quantity = 0

            # append barcode to list quantity number of times
            while quantity > 0:
                if store not in store_dict:
                    store_dict[store] = []
                store_tuple = (order_number, barcode)
                store_dict[store].append(store_tuple)
                quantity = quantity - 1
    
    # remove store 99 from the dictionary because those items do not need to be RMAd
    store_dict.pop('99')
    return store_dict

main()