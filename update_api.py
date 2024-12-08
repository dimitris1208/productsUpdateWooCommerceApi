import requests
from dotenv import load_dotenv
import os

load_dotenv()

# WooCommerce API credentials
WP_API_BASE_URL = os.getenv("WP_API_BASE_URL")
WP_API_CONSUMER_KEY = os.getenv("WP_API_CONSUMER_KEY")
WP_API_CONSUMER_SECRET = os.getenv("WP_API_CONSUMER_SECRET")



def update_product_price(sku, new_price):
    """
    Updates the price of a product in WooCommerce using its SKU.
    :param sku: SKU of the product to update.
    :param new_price: The new price to set for the product.
    :return: Response from the WooCommerce API.
    """
    try:
        # Fetch the product ID using the SKU
        response = requests.get(
            WP_API_BASE_URL,
            params={
                "sku": sku,
                "consumer_key": WP_API_CONSUMER_KEY,
                "consumer_secret": WP_API_CONSUMER_SECRET,
            },
            timeout=30,
        )
        response.raise_for_status()
        products = response.json()

        # If no products are found, raise an exception
        if not products:
            print(f"No product found with SKU: {sku}")
            return None

        # Get the product ID from the first matching product
        product_id = products[0]["id"]

        # Update the product's price
        update_url = f"{WP_API_BASE_URL}/{product_id}"
        update_response = requests.put(
            update_url,
            json={"regular_price": str(new_price)},  # WooCommerce expects price as a string
            auth=(WP_API_CONSUMER_KEY, WP_API_CONSUMER_SECRET),
            timeout=30,
        )
        update_response.raise_for_status()

        print(f"Price for SKU {sku} updated to {new_price}.")
        return update_response.json()

    except requests.RequestException as e:
        print(f"Error updating product price for SKU {sku}: {e}")
        return None














def delete_product(sku):
    """
    Deletes a product in WooCommerce using its SKU.
    :param sku: SKU of the product to delete.
    :return: Response from the WooCommerce API.
    """
    try:
        # Fetch the product ID using the SKU
        response = requests.get(
            WP_API_BASE_URL,
            params={
                "sku": sku,
                "consumer_key": WP_API_CONSUMER_KEY,
                "consumer_secret": WP_API_CONSUMER_SECRET,
            },
            timeout=30,
        )
        response.raise_for_status()
        products = response.json()

        # If no products are found, raise an exception
        if not products:
            print(f"No product found with SKU: {sku}")
            return None

        # Get the product ID from the first matching product
        product_id = products[0]["id"]

        # Delete the product using the product ID
        delete_url = f"{WP_API_BASE_URL}/{product_id}"
        delete_response = requests.delete(
            delete_url,
            auth=(WP_API_CONSUMER_KEY, WP_API_CONSUMER_SECRET),
            timeout=30,
        )
        delete_response.raise_for_status()

        print(f"Product with SKU {sku} successfully deleted.")
        return delete_response.json()

    except requests.RequestException as e:
        print(f"Error deleting product with SKU {sku}: {e}")
        return None




