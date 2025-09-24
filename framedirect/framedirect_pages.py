"""
Modular version of framedirect.py.
This script scrapes products on framedirect.com/eyeglasses with basic details.
"""

# Import necessary libraries
import csv
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional


def setup_webdriver() -> webdriver.Chrome:
    """
    Configure and initialize Chrome WebDriver with appropriate options.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    print("Setting up webdriver...")

    chrome_option = Options()
    # Temporarily disable headless mode for better debugging
    # chrome_option.add_argument("--headless")  # Comment out for debugging
    chrome_option.add_argument("--disable-gpu")
    chrome_option.add_argument("--no-sandbox")
    chrome_option.add_argument("--disable-dev-shm-usage")
    chrome_option.add_argument("--disable-blink-features=AutomationControlled")
    chrome_option.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_option.add_experimental_option("useAutomationExtension", False)
    chrome_option.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
    )
    print("Done setting up options...")

    # Install the chrome driver
    print("Installing Chrome WebDriver...")
    service = Service(ChromeDriverManager().install())

    print("Initializing WebDriver...")
    driver = webdriver.Chrome(service=service, options=chrome_option)
    print("WebDriver setup complete")

    return driver


def fetch_page_content(
    driver: webdriver.Chrome, url: str, timeout: int = 15
) -> Optional[str]:
    """
    Navigate to URL and wait for page content to load.

    Args:
        driver: Chrome WebDriver instance
        url: URL to navigate to
        timeout: Timeout in seconds to wait for page load

    Returns:
        str: Page source HTML if successful, None if failed
    """
    print(f"Visiting {url} page...")

    try:
        driver.get(url)

        print("Waiting for product tiles to load...")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "product-list-container"))
        )
        print("Page loaded successfully, proceeding to parse data...")

        return driver.page_source

    except Exception as e:
        print(f"Error waiting for {url}: {e}")
        return None


def extract_brand_info(holder) -> Optional[str]:
    """
    Extract brand information from product holder.

    Args:
        holder: BeautifulSoup element containing product information

    Returns:
        str: Brand name if found, None otherwise
    """
    product_info = holder.find("div", class_="catalog-container")
    if product_info:
        brand_tag = product_info.find("div", class_="catalog-name")
        return brand_tag.text.strip() if brand_tag else None
    return None


def extract_product_name(holder) -> Optional[str]:
    """
    Extract product name from product holder.

    Args:
        holder: BeautifulSoup element containing product information

    Returns:
        str: Product name if found, None otherwise
    """
    name_tag = holder.find("div", class_="product_name")
    return name_tag.text.strip() if name_tag else None


def extract_discount_info(holder) -> Optional[str]:
    """
    Extract discount information from product holder.

    Args:
        holder: BeautifulSoup element containing product information

    Returns:
        str: Discount information if found, None otherwise
    """
    discount_tag = holder.find("div", class_="frame-discount")
    if discount_tag:
        discount_text = discount_tag.get_text(strip=True).replace("\xa0", "")
        return discount_text if discount_text else None
    return None


def extract_price_info(holder) -> tuple:
    """
    Extract retail and discounted price information from product holder.

    Args:
        holder: BeautifulSoup element containing product information

    Returns:
        tuple: (retail_price, discounted_price) - both can be None if not found
    """
    retail_price = None
    discounted_price = None

    price_cnt = holder.find("div", class_="prod-price-wrap")
    if price_cnt:
        # Extract retail price
        retail_price_tag = price_cnt.find("div", class_="prod-catalog-retail-price")
        if retail_price_tag:
            match = re.findall(r"[\d,.]+", retail_price_tag.text)
            retail_price = match[0].replace(",", "") if match else None

        # Extract discounted price
        discounted_price_tag = price_cnt.find("div", class_="prod-aslowas")
        if discounted_price_tag:
            match = re.findall(r"[\d,.]+", discounted_price_tag.text)
            discounted_price = match[0].replace(",", "") if match else None

    return retail_price, discounted_price


def close_overlays(driver: webdriver.Chrome) -> None:
    """
    Close any overlays or popups that might interfere with navigation.

    Args:
        driver: Chrome WebDriver instance
    """
    try:
        # Close fancybox overlay
        overlay = driver.find_element(By.CSS_SELECTOR, ".fancybox-overlay")
        if overlay.is_displayed():
            print("Found fancybox overlay, closing it...")
            driver.execute_script("jQuery.fancybox.close();")
            time.sleep(1)
    except:
        pass

    try:
        # Close any modal dialogs
        close_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            ".fancybox-close, .modal-close, .close, [aria-label='Close']",
        )
        for btn in close_buttons:
            if btn.is_displayed():
                btn.click()
                time.sleep(0.5)
    except:
        pass

    try:
        # Press ESC to close any modal
        from selenium.webdriver.common.keys import Keys

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.5)
    except:
        pass


def navigate_to_next_page(driver: webdriver.Chrome, timeout: int = 15) -> bool:
    """
    Navigate to the next page using the next page button.

    Args:
        driver: Chrome WebDriver instance
        timeout: Timeout in seconds to wait for navigation

    Returns:
        bool: True if successfully navigated to next page, False otherwise
    """
    print("Looking for next page button...")

    # Store current URL to verify navigation
    current_url = driver.current_url
    current_page_num = get_current_page_number(driver)

    try:
        # Multiple strategies to find the next button
        next_button = None

        # Strategy 1: Try aria-label="next page"
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'a[aria-label="next page"]')
                )
            )
            print("Found next button using aria-label='next page'")
        except:
            pass

        # Strategy 2: Try different aria-label variations
        if not next_button:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'a[aria-label="nextpage"]')
                    )
                )
                print("Found next button using aria-label='nextpage'")
            except:
                pass

        # Strategy 3: Try by class and text content
        if not next_button:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//a[contains(@class, 'icon-cheveron-right') or contains(text(), 'next') or contains(@href, 'p=')]",
                        )
                    )
                )
                print("Found next button using class/text content")
            except:
                pass

        # Strategy 4: Try finding by href pattern (p=X)
        if not next_button:
            try:
                # Look for link with p= parameter that's greater than current page
                next_page_num = current_page_num + 1
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//a[contains(@href, 'p={next_page_num}')]")
                    )
                )
                print(f"Found next button using href pattern for page {next_page_num}")
            except:
                pass

        if not next_button:
            print("Could not find next page button with any strategy")
            return False

        # Get the href before clicking
        next_href = next_button.get_attribute("href")
        print(f"Next button href: {next_href}")

        # Check if the button has a valid href
        if not next_href or "javascript:" in next_href:
            print("Next button has no valid href or is disabled")
            return False

        # Close any overlays first
        close_overlays(driver)

        # Multiple click strategies
        click_successful = False

        # Strategy 1: JavaScript click (bypasses overlays)
        try:
            print("Attempting JavaScript click...")
            driver.execute_script("arguments[0].click();", next_button)
            click_successful = True
            print("JavaScript click successful")
        except Exception as js_error:
            print(f"JavaScript click failed: {js_error}")

        # Strategy 2: Direct navigation using href
        if not click_successful:
            try:
                print("Attempting direct navigation using href...")
                driver.get(next_href)
                click_successful = True
                print("Direct navigation successful")
            except Exception as nav_error:
                print(f"Direct navigation failed: {nav_error}")

        # Strategy 3: Regular click as last resort
        if not click_successful:
            try:
                print("Attempting regular click after closing overlays...")
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", next_button
                )
                time.sleep(1)
                close_overlays(driver)  # Close overlays again
                next_button.click()
                click_successful = True
                print("Regular click successful")
            except Exception as click_error:
                print(f"Regular click failed: {click_error}")

        if not click_successful:
            print("All click strategies failed")
            return False

        # Wait for navigation
        print("Waiting for page navigation...")
        time.sleep(3)

        # Wait for new page to load
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, "product-list-container"))
            )
        except:
            print("Warning: Product container not found, but continuing...")

        # Verify that we actually navigated
        new_url = driver.current_url
        new_page_num = get_current_page_number(driver)

        if new_url != current_url or new_page_num > current_page_num:
            print(f"Successfully navigated to page {new_page_num}")
            return True
        else:
            print(f"Navigation failed - still on same page {current_page_num}")
            return False

    except Exception as e:
        print(f"Error navigating to next page: {e}")
        print(f"Current URL: {driver.current_url}")

        # Debug: Print available links
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(links)} links on page")
            for link in links[:10]:  # Show first 10 links for debugging
                href = link.get_attribute("href")
                text = link.text.strip()
                aria_label = link.get_attribute("aria-label")
                if href and ("p=" in href or "next" in text.lower() or aria_label):
                    print(
                        f"  Link: href='{href}', text='{text}', aria-label='{aria_label}'"
                    )
        except:
            pass

        return False


def get_current_page_number(driver: webdriver.Chrome) -> int:
    """
    Extract current page number from the URL or page elements.

    Args:
        driver: Chrome WebDriver instance

    Returns:
        int: Current page number, defaults to 1 if not found
    """
    try:
        current_url = driver.current_url
        # Extract page number from URL pattern: ?p=2&type=pagestate
        if "p=" in current_url:
            import re

            match = re.search(r"p=(\d+)", current_url)
            if match:
                return int(match.group(1))
        return 1
    except:
        return 1


def parse_product_data(page_source: str) -> List[Dict]:
    """
    Parse product data from HTML page source.

    Args:
        page_source: HTML source code of the page

    Returns:
        List[Dict]: List of dictionaries containing product information
    """
    page = BeautifulSoup(page_source, "html.parser")
    glasses_data = []

    # Locate all product holders
    product_holders = page.find_all("div", class_="prod-holder")
    print(f"Found {len(product_holders)} products")

    for holder in product_holders:
        # Extract all product information
        brand = extract_brand_info(holder)
        name = extract_product_name(holder)
        discount = extract_discount_info(holder)
        retail_price, discounted_price = extract_price_info(holder)

        # Collect extracted data
        data = {
            "Brand": brand,
            "Product_Name": name,
            "Retail_Price": retail_price,
            "Discounted_Price": discounted_price,
            "Discount": discount,
        }
        glasses_data.append(data)

    return glasses_data


def save_to_csv(
    data: List[Dict], filename: str = "pagedata/framedirect_data2.csv"
) -> bool:
    """
    Save product data to CSV file.

    Args:
        data: List of dictionaries containing product information
        filename: Name of the CSV file to save

    Returns:
        bool: True if successful, False otherwise
    """
    if not data:
        print("No data found, CSV not created.")
        return False

    try:
        # Create directory if it doesn't exist
        import os

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        column_names = data[0].keys()
        with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
            dict_writer = csv.DictWriter(csv_file, fieldnames=column_names)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Data saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return False


def save_to_json(
    data: List[Dict], filename: str = "pagedata/framedirect_data2.json"
) -> bool:
    """
    Save product data to JSON file.

    Args:
        data: List of dictionaries containing product information
        filename: Name of the JSON file to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        import os

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, mode="w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Saved {len(data)} records to {filename}")
        return True
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False


def cleanup_driver(driver: webdriver.Chrome) -> None:
    """
    Clean up and close the WebDriver.

    Args:
        driver: Chrome WebDriver instance to close
    """
    driver.quit()
    print("Browser closed")


def scrape_framedirect_eyeglasses(
    url: str = "https://www.framesdirect.com/eyeglasses/",
    csv_filename: str = "pagedata/framedirect_data2.csv",
    json_filename: str = "pagedata/framedirect_data2.json",
    max_pages: int = 1,
) -> List[Dict]:
    """
    Main function to scrape eyeglasses data from framedirect.com

    Args:
        url: URL to scrape from
        csv_filename: Name for CSV output file
        json_filename: Name for JSON output file
        max_pages: Maximum number of pages to scrape (default: 1)

    Returns:
        List[Dict]: List of dictionaries containing product information
    """
    driver = None
    all_glasses_data = []

    try:
        # Step 1: Setup WebDriver
        driver = setup_webdriver()

        # Step 2: Start scraping from first page
        page_source = fetch_page_content(driver, url)
        if not page_source:
            print("Failed to fetch page content")
            return []

        pages_scraped = 0

        # Step 3: Loop through pages
        while pages_scraped < max_pages:
            current_page = get_current_page_number(driver)
            print(f"\n--- Scraping Page {current_page} ---")

            # Get current page source
            if pages_scraped == 0:
                # Use the already fetched page source for first page
                current_page_source = page_source
            else:
                current_page_source = driver.page_source

            # Parse product data from current page
            page_data = parse_product_data(current_page_source)

            if page_data:
                all_glasses_data.extend(page_data)
                print(f"Scraped {len(page_data)} products from page {current_page}")
            else:
                print(f"No products found on page {current_page}")

            pages_scraped += 1

            # Check if we need to navigate to next page
            if pages_scraped < max_pages:
                print(
                    f"\n🔄 Attempting to navigate from page {current_page} to page {current_page + 1}..."
                )
                print(f"Current URL: {driver.current_url}")

                navigation_success = navigate_to_next_page(driver)

                if navigation_success:
                    print(f"✅ Successfully navigated to next page")
                    # Verify we're actually on a new page
                    new_page_num = get_current_page_number(driver)
                    print(f"New page number: {new_page_num}")
                    print(f"New URL: {driver.current_url}")
                else:
                    print("❌ Could not navigate to next page or reached last page")
                    print("This might be the last available page or navigation failed")
                    break

                # Small delay between page navigations
                print("⏳ Waiting before next page...")
                time.sleep(3)

        print(f"\n=== Scraping Summary ===")
        print(f"Pages scraped: {pages_scraped}")
        print(f"Total products found: {len(all_glasses_data)}")

        # Step 4: Save data to files
        if all_glasses_data:
            save_to_csv(all_glasses_data, csv_filename)
            save_to_json(all_glasses_data, json_filename)
        else:
            print("No data to save")

        return all_glasses_data

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return all_glasses_data

    finally:
        # Step 5: Cleanup
        if driver:
            cleanup_driver(driver)
        print("End of Web Extraction")


def get_user_input_for_pages() -> int:
    """
    Get user input for number of pages to scrape.

    Returns:
        int: Number of pages to scrape
    """
    while True:
        try:
            pages = input(
                "\nHow many pages would you like to scrape? (Enter a number, default=1): "
            ).strip()

            if not pages:  # If user just presses Enter
                return 1

            pages = int(pages)

            if pages < 1:
                print("Please enter a number greater than 0")
                continue
            elif pages > 100:  # Safety limit
                confirm = input(
                    f"You want to scrape {pages} pages. This might take a long time. Continue? (y/n): "
                )
                if confirm.lower() in ["y", "yes"]:
                    return pages
                else:
                    continue
            else:
                return pages

        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 0


# Main execution block
if __name__ == "__main__":
    """
    Main execution when script is run directly.
    """
    print("=== FrameDirect Eyeglasses Scraper ===")

    # Direct page control - Change this number to scrape different number of pages
    PAGES_TO_SCRAPE = 3  # ← CHANGE THIS NUMBER TO SCRAPE MORE/FEWER PAGES

    print(f"Configured to scrape {PAGES_TO_SCRAPE} page(s) of eyeglasses data.")
    print(f"Starting scrape for {PAGES_TO_SCRAPE} page(s)...")

    scraped_data = scrape_framedirect_eyeglasses(max_pages=PAGES_TO_SCRAPE)
    print(f"\nScraping completed. Total products scraped: {len(scraped_data)}")
