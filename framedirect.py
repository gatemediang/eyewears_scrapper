"""
This script scrapes products on framedirect.com/eyeglasses with basic details.
"""

import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

# Step 1 - Configuration and Data Fetching
print("Setting up webdriver...")
chrome_option = Options()
chrome_option.add_argument("--headless")
chrome_option.add_argument("--disable-gpu")
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)
print("done setting up..")

# Install the chrome driver (This is a one time thing)
print("Installing Chrome WD")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_option)
print("Done")

# Make connection and get URL content
url = "https://www.framesdirect.com/eyeglasses/"
print(f"Visting {url} page")
driver.get(url)

# Further instruction: wait for JS to load the files
try:
    print("Waiting for product tiles to load")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "product-list-container"))
    )
    print("Done...Proceed to parse the data")
except (TimeoutError, Exception) as e:
    print(f"Error waiting for {url}: {e}")
    driver.quit()
    print("Closed")

# Get page source and parse using BeautifulSoup
content = driver.page_source
page = BeautifulSoup(content, "html.parser")

# Temporary storage for the extracted data
glasses_data = []

# Locate all product holders and extract the data for each product.
product_holders = page.find_all("div", class_="prod-holder")
print(f"Found {len(product_holders)} products")

for holder in product_holders:
    product_info = holder.find("div", class_="catalog-container")
    if product_info:
        brand_tag = product_info.find("div", class_="catalog-name")
        brand = brand_tag.text.strip() if brand_tag else None  # product brand
    else:
        brand = None

    # Product Name
    name_tag = holder.find("div", class_="product_name")
    name = name_tag.text.strip() if name_tag else None

    # Discount (force None if empty or only whitespace)
    discount_tag = holder.find("div", class_="frame-discount")
    if discount_tag:
        discount_text = discount_tag.get_text(strip=True).replace("\xa0", "")
        discount = discount_text if discount_text else None
    else:
        discount = None

    # Prices
    price_cnt = holder.find("div", class_="prod-price-wrap")
    if price_cnt:
        # Retail Price
        retail_price_tag = price_cnt.find("div", class_="prod-catalog-retail-price")
        if retail_price_tag:
            match = re.findall(r"[\d,.]+", retail_price_tag.text)
            retail_price = match[0].replace(",", "") if match else None
        else:
            retail_price = None

        # Discounted Price
        discounted_price_tag = price_cnt.find("div", class_="prod-aslowas")
        if discounted_price_tag:
            match = re.findall(r"[\d,.]+", discounted_price_tag.text)
            discounted_price = match[0].replace(",", "") if match else None
        else:
            discounted_price = None
    else:
        retail_price = None
        discounted_price = None

    # Collect extracted data
    data = {
        "Brand": brand,
        "Product_Name": name,
        "Retail_Price": retail_price,
        "Discounted_Price": discounted_price,
        "Discount": discount,
    }
    glasses_data.append(data)

# Save to CSV file
if glasses_data:  # only proceed if list is not empty
    column_name = glasses_data[0].keys()
    with open(
        "framedirect_data.csv", mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=column_name)
        dict_writer.writeheader()
        dict_writer.writerows(glasses_data)
    print("Data saved to framedirect_data.csv")
else:
    print("No data found, CSV not created.")

# Save to JSON file
with open("framedirect_data.json", mode="w") as json_file:
    json.dump(glasses_data, json_file, indent=4)
print(f"Saved {len(glasses_data)} records to JSON")

# close the browser
driver.quit()
print("End of Web Extraction")
