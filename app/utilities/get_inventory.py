import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
from app.config import PRODUCT_INFO_ENDPOINT, PRODUCT_AVAILABILITY_ENDPOINT, API_ACCOUNT_ID, API_APPLICATION_KEY, FILE_NEW_INVENTORY
from app.utilities.inventory_upload import upload_inventory_files

def prettify(element, indent='  '):
    queue = [(0, element)]  # (level, element)
    while queue:
        level, element = queue.pop(0)
        children = list(element)
        if children:
            element.text = '\n' + indent * (level+1)  # for child open
        if element.tail is None:
            element.tail = '\n' + indent * level  # for close
        for child in reversed(children):
            queue.insert(0, (level + 1, child))

def run_inventory_update():
    # Function to get current date-time string
    def get_datetime_string():
        return datetime.now().strftime("%Y%m%d-%H%M")

    # Use the imported config values
    product_url = PRODUCT_INFO_ENDPOINT
    availability_base_url = PRODUCT_AVAILABILITY_ENDPOINT
    headers = {
        'api-auth-accountid': API_ACCOUNT_ID,
        'api-auth-applicationkey': API_APPLICATION_KEY
    }

    # Generate advice file control number and file name with current date-time
    datetime_str = get_datetime_string()
    control_number = f"{datetime_str}-0001"
    file_name = f"product_availabilities_{datetime_str}.xml"

    # Create the root XML element
    root = ET.Element('advice_file', attrib={
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
        "xsi:noNamespaceSchemaLocation": ".\\XMLGuides\\HubXML%20Costco%20Inventory.xsd"
    })
    ET.SubElement(root, 'advice_file_control_number').text = control_number
    ET.SubElement(root, 'vendor').text = "orionisca"
    ET.SubElement(root, 'vendorMerchID').text = "costco"

    response = requests.get(product_url, headers=headers)
    products_count = 0

    if response.status_code == 200:
        data = response.json()
        filtered_entries = [product for product in data['Products'] if product.get('Tags') == 'COSTCOE']

        for product in filtered_entries:
            sku = product['SKU']
            name = product.get('Name', 'No Name Provided')
            additional_attribute2 = product.get('AdditionalAttribute2', 'N/A')
            unit_cost = product.get("PriceTiers", {}).get("Tier 1 - Wholesale", "N/A")
            
            product_element = ET.SubElement(root, 'product')
            ET.SubElement(product_element, 'vendor_SKU').text = sku
            ET.SubElement(product_element, 'description').text = name
            ET.SubElement(product_element, 'merchantSKU').text = additional_attribute2
            ET.SubElement(product_element, 'unit_cost').text = str(unit_cost)

            response = requests.get(f"{availability_base_url}{sku}", headers=headers)
            qtyonhand = "0"  # Default quantity
            available = "YES"  # Assume availability

            if response.status_code == 200:
                product_availability_response = response.json()
                for item in product_availability_response.get('ProductAvailabilityList', []):
                    if item.get('Location') == 'OTC_WH':
                        qtyonhand = str(item.get('Available', 0))
                        break

            ET.SubElement(product_element, 'qtyonhand').text = qtyonhand
            ET.SubElement(product_element, 'available').text = available

            warehouse_breakout = ET.SubElement(product_element, 'warehouseBreakout')
            warehouse = ET.SubElement(warehouse_breakout, 'warehouse', attrib={"warehouse-id": "OTC Fulfillment Center"})
            ET.SubElement(warehouse, 'qtyonhand').text = qtyonhand

            products_count += 1

        ET.SubElement(root, 'advice_file_count').text = str(products_count)

        # Use the prettify function to format the XML
        prettify(root)

        # Generate and save the XML file
        tree = ET.ElementTree(root)
        file_path = os.path.join(FILE_NEW_INVENTORY, file_name)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        print(f"Filtered product availabilities have been saved to {file_path}")
        upload_inventory_files()


    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

if __name__ == "__main__":
    run_inventory_update()