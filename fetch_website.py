import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import re
from category_urls import category_urls

# Base URL for the website
BASE_URL = "https://www.your_website.gr"

# Retry settings
MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds

# Number of threads
NUM_THREADS = 4

# Output CSV file
OUTPUT_FILE = "website_products.csv"


def fetch_page(url):
    """
    Fetch a page's content using requests with retries.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}. Retrying ({attempt + 1}/{MAX_RETRIES})...")
            if attempt + 1 < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    print(f"Failed to fetch URL after {MAX_RETRIES} attempts: {url}")
    return None


def clean_price(price):
    """
    Clean the price string: remove non-numeric characters, replace commas with dots,
    and convert it to a float if valid.
    """
    if not price:
        return None

    # Remove non-numeric characters except for commas and periods
    price = re.sub(r"[^\d.,]", "", price)

    # Replace commas with periods for decimal conversion
    price = price.replace(",", ".")

    # Remove thousands separators (periods) except for the last one (decimal point)
    price = re.sub(r"(?<=\d)\.(?=\d{3})", "", price)

    try:
        return float(price)
    except ValueError:
        return None


def fetch_category_skus_prices(category_url):
    """
    Fetch SKUs and prices for all products listed on the category page, handling pagination.
    """
    products = []

    # Fetch the first page to determine the total number of pages
    html = fetch_page(category_url)
    if not html:
        return products

    soup = BeautifulSoup(html, "html.parser")

    # Extract the total number of pages from the pagination
    pagination = soup.find("div", id="pagination")
    if pagination:
        page_links = pagination.find_all("a", class_="num")
        total_pages = int(page_links[-1].text) if page_links else 1  # Default to 1 page if no pagination links
    else:
        total_pages = 1

    # Fetch products from each page
    for page_number in range(1, total_pages + 1):
        paginated_url = f"{category_url}?p={page_number}"
        print(f"Fetching page {page_number} of {total_pages}: {paginated_url}")
        html = fetch_page(paginated_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        # Find all product containers
        product_containers = soup.select("div.prdv div.prd")
        for container in product_containers:
            # Extract SKU
            sku_element = container.find("h4")
            sku = sku_element.text.strip() if sku_element else "N/A"

            # Extract price
            price_element = container.find("p", class_="prc")
            regular_price = None

            if price_element:
                # Try to extract the regular price from the <span> element
                regular_price_span = price_element.find("span")
                if regular_price_span and regular_price_span.text.strip():
                    regular_price = clean_price(regular_price_span.text.strip())
                else:
                    # Fallback to data-price attribute
                    regular_price = clean_price(price_element.get("data-price"))

            # Add product details to the list
            products.append({
                "sku": sku,
                "regular_price": regular_price,
            })

    return products


def fetch_all_categories_skus_prices(category_urls):
    """
    Fetch SKUs and prices for all categories using multithreading.
    """
    all_products = []
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(fetch_category_skus_prices, url) for url in category_urls]
        for future in futures:
            all_products.extend(future.result())
    return all_products


def remove_duplicates(file_path):
    """
    Remove duplicate rows in the CSV file based on the SKU column.
    Overwrites the file with the deduplicated data.
    """
    print("Removing duplicate rows based on SKU...")
    try:
        # Load the CSV into a DataFrame
        df = pd.read_csv(file_path)

        # Remove duplicates by SKU, keeping the first occurrence
        df_deduplicated = df.drop_duplicates(subset="sku", keep="first")

        # Save the deduplicated data back to the CSV
        df_deduplicated.to_csv(file_path, index=False, encoding="utf-8")
        print(f"Duplicates removed. Deduplicated data saved to {file_path}")
    except Exception as e:
        print(f"Error during duplicate removal: {e}")



def main():

    print("Starting to fetch SKUs and regular prices from Website...")
    all_products = fetch_all_categories_skus_prices(category_urls)

    # Save products to a CSV file
    df = pd.DataFrame(all_products)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"Fetching completed. Data saved to {OUTPUT_FILE}")
    remove_duplicates(OUTPUT_FILE)
    print("COMPLETE")

if __name__ == "__main__":
    main()
