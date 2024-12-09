from update_api import update_product_price , delete_product , create_new_product
import pandas as pd

# File paths for the CSV files
WEBSITE_FILE = "website_products.csv"
WOOCOMMERCE_FILE = "woocommerce_products.csv"


def compare_products():
    """
    Compares the products from website with WooCommerce and takes necessary actions.
    Updates the flag column for matched products and deletes unmatched products.
    """
    # Load the CSV files
    try:
        website_data = pd.read_csv(WEBSITE_FILE)
        woocommerce_data = pd.read_csv(WOOCOMMERCE_FILE)
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return

    # Ensure the 'flag' column exists and is initialized to 0
    if "flag" not in woocommerce_data.columns:
        woocommerce_data["flag"] = 0

    # Convert WooCommerce data to a dictionary for faster lookup by SKU
    woocommerce_dict = woocommerce_data.set_index("sku").to_dict("index")

    # Iterate through Website products
    for _, row in website_data.iterrows():
        website_sku = row["sku"]
        website_price = row["regular_price"]

        # Check if SKU exists in WooCommerce
        if website_sku in woocommerce_dict:
            woocommerce_price = woocommerce_dict[website_sku]["price"]

            # Compare prices
            if website_price != woocommerce_price:
                # Call function to update product price
                update_product_price(website_sku, website_price)

            # Update the flag to 1 for matched products
            woocommerce_data.loc[woocommerce_data["sku"] == website_sku, "flag"] = 1
        else:
            # SKU not found in WooCommerce, create a new product
            create_new_product(website_sku, website_price)

    # Handle unmatched products in WooCommerce (flag = 0)
    unmatched_products = woocommerce_data[woocommerce_data["flag"] == 0]
    for _, row in unmatched_products.iterrows():
        delete_product(row["sku"])

    # Save the updated WooCommerce data back to the CSV
    woocommerce_data.to_csv(WOOCOMMERCE_FILE, index=False, encoding="utf-8")
    print("Comparison completed. WooCommerce CSV updated .")


if __name__ == "__main__":
    compare_products()
