import requests
import pandas as pd
from dotenv import load_dotenv
from fetch_website import remove_duplicates
import os

load_dotenv()

# WooCommerce API credentials
WP_API_BASE_URL = os.getenv('WP_API_BASE_URL')
WP_API_CONSUMER_KEY = os.getenv('WP_API_CONSUMER_KEY')
WP_API_CONSUMER_SECRET = os.getenv('WP_API_CONSUMER_SECRET')

# Output CSV file
OUTPUT_FILE = "woocommerce_products.csv"

def fetch_woocommerce_products():
    """
    Fetches all products from WooCommerce using the REST API.
    Returns a list of products, where each product is a dictionary.
    """
    products = []
    page = 1

    while True:
        print(f"Fetching page {page} of WooCommerce products...")
        try:
            response = requests.get(
                WP_API_BASE_URL,
                params={
                    "page": page,
                    "per_page": 100,  # Maximum items per page
                    "consumer_key": WP_API_CONSUMER_KEY,
                    "consumer_secret": WP_API_CONSUMER_SECRET,
                },
                timeout=30
            )
            response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
            data = response.json()
            if not data:  # If no data is returned, we've reached the last page
                break
            products.extend(data)
            page += 1
        except requests.RequestException as e:
            print(f"Error fetching products: {e}")
            break

    print(f"Total products fetched: {len(products)}")
    return products

def save_skus_and_prices_to_csv(products):
    """
    Saves the SKUs and prices of WooCommerce products into a CSV file.
    :param products: List of product dictionaries fetched from WooCommerce.
    """
    # Extract SKU and price information
    product_data = []
    for product in products:
        sku = product.get("sku", "N/A")
        price = product.get("price", "N/A")
        product_data.append({"sku": sku, "price": price , "flag" : 0})

    # Save to a CSV file
    df = pd.DataFrame(product_data)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"SKUs and prices saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    # Fetch products from WooCommerce
    all_products = fetch_woocommerce_products()

    # Save SKUs and prices to CSV
    save_skus_and_prices_to_csv(all_products)
    remove_duplicates(OUTPUT_FILE)
    print("COMPLETE")
