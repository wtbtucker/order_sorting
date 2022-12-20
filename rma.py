from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException 
import os
import csv
# TODO: fix store number with sku in notes

driver = webdriver.Edge()
receive_path = 'C:\\Users\\wtbtu\\Documents\\marathon_sports\\order_sorting\\99 scan upload.txt'
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

    # create file to be received into store 99 and dictionary with the items to be removed from individual stores
    store_dict, barcode_list = create_store_dict()
    print(store_dict)

    write_receive_file(barcode_list)

    login()
    navigate_store('99') 
    receive_file()
    navigate_rma()

    # iterate through list of stores as keys
    for store in store_dict:
        navigate_store(store)
        
        # navigate to 'Scanning' tab
        navigate_menu('ctl00_ContentPlaceHolder1_btnScanView')

        # Use order number and barcode to remove each line item assigned to a particular store
        for line_item in store_dict[store]:
            # Enter Shopify order number in 'RMA Number' field
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtRmaNumber').clear()
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtRmaNumber').send_keys(line_item[0])
            # enter product barcode into UPC field
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_productEntryList_txtIdentifier').send_keys(line_item[1])
            driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_productEntryList_txtIdentifier').send_keys(Keys.RETURN)

            # add entry and save
            navigate_menu('ctl00_ContentPlaceHolder1_productEntryList_btnAddToList')
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
    storeInputElement = driver.find_element(By.ID, 'ctl00_otxtQuickOrganizationNavigation_txtOrganizationCriteriaEntry')
    storeInputElement.send_keys(store_number)

    # Wait until the placeholder disappears from the store code input
    WebDriverWait(driver, timeout=10).until(EC.none_of(EC.text_to_be_present_in_element((By.ID,'ctl00_otxtQuickOrganizationNavigation_txtOrganizationCriteriaEntry'), 'Store Code')))
    storeInputElement.send_keys(Keys.RETURN)

    # Wait until page loads with the correct store number at top
    WebDriverWait(driver, timeout=10).until(EC.text_to_be_present_in_element((By.ID, 'ctl00_lblOrganization'), store_number))


# Select 'inventory', 'stock maintenance', then 'Enter Returns to Supplier (RMA)'
def navigate_rma():
    navigate_menu('ctl00_btnStock')
    navigate_menu('n3')
    navigate_menu('n14')

# Select 'inventory', 'receiving', 'receive stock without PO', 'upload', then 'Upload From File'
def navigate_receive():
    navigate_menu('ctl00_btnStock')
    navigate_menu('n22')
    navigate_menu('n25')

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
    # initialize dictionary for receipt and list for RMA
    store_dict = {}
    barcode_list = []

    # open the orders csv file and create reader object
    path = os.path.dirname(os.path.realpath(__file__))
    orders_path = path + "\\orders.csv"
    with open(orders_path, "r") as o:
        reader = csv.DictReader(o)

        # create dictionary with stores as keys and barcodes as values
        # create list of barcodes to be received into store 99
        for row in reader:
            store = row["Note"]
            barcode = row["Product barcode"]
            order_number = row["Order number"]

            # convert quantity to integer if not blank
            if row["Line item quantity"]:
                quantity = int(row["Line item quantity"])
            else:
                quantity = 0

            # items from store 99 and fba do not need to be adjusted (RMAed or received)
            if store != "99" and store != "fba":
                while quantity > 0:
                    if store not in store_dict:
                        store_dict[store] = []
                    store_tuple = (order_number, barcode)
                    store_dict[store].append(store_tuple)
                    barcode_list.append(barcode)
                    quantity = quantity - 1
    
    return store_dict, barcode_list

def write_receive_file(barcode_list):
    global receive_path
    # formatting (blank first line, tab delineated with '01') required for RICS upload
    with open(receive_path, 'w') as output:
        output.write('\n') 
        for barcode in barcode_list:
            output.write(barcode)
            output.write("\t")
            output.write("01")
            output.write("\n")

def receive_file():
    global receive_path
    global driver

    navigate_receive()

    # Select 'Upload', then 'Upload From File'
    navigate_menu('ctl00_ContentPlaceHolder1_btnUploadView')
    navigate_menu('ctl00_ContentPlaceHolder1_portableReaderInterface_radioFile')

    # Enter the path for the receive file into the browse field and submit
    pathElement = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_portableReaderInterface_txtFilePath')
    pathElement.send_keys(receive_path)
    navigate_menu('ctl00_ContentPlaceHolder1_portableReaderInterface_btnUploadFromFile')

    WebDriverWait(driver, timeout=10).until(EC.text_to_be_present_in_element((By.ID, 'ctl00_ContentPlaceHolder1_portableReaderInterface_lblUploadStatus'), 'The file has been received by the server. Processing...'))
    navigate_menu('ctl00_ContentPlaceHolder1_btnScanView')
    navigate_menu('ctl00_cmdMaster5')

def wait_present(id):
    global driver

    try: 
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, id))
        )
    finally:
        driver.quit()

main()