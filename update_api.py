import requests
from dotenv import load_dotenv
import os
import re
from bs4 import BeautifulSoup

load_dotenv()

# WooCommerce API credentials
WP_API_BASE_URL = os.getenv("WP_API_BASE_URL")
WP_API_CONSUMER_KEY = os.getenv("WP_API_CONSUMER_KEY")
WP_API_CONSUMER_SECRET = os.getenv("WP_API_CONSUMER_SECRET")


#------------------------------------------------------------------------------------------------------------


BASE_URL = "https://www.your_website.gr"



def scrape_product_details(sku):
    """
    Scrape details of a single product by SKU.
    :param sku: SKU of the product to scrape.
    :return: Dictionary containing product details.
    """
    search_url = f"{BASE_URL}/search?q={sku}"
    try:
        # Fetch the search page
        search_response = requests.get(search_url, timeout=30)
        search_response.raise_for_status()
        search_soup = BeautifulSoup(search_response.text, "html.parser")

        # Find the link to the product page
        product_link_tag = search_soup.select_one("div.prdv a[href]")
        if not product_link_tag:
            print(f"Product with SKU {sku} not found on the website.")
            return None

        product_url = BASE_URL + product_link_tag["href"]

        # Fetch the product page
        product_response = requests.get(product_url, timeout=30)
        product_response.raise_for_status()
        product_soup = BeautifulSoup(product_response.text, "html.parser")

        # Extract product details
        # Title
        title = product_soup.find("h1").text.strip()

        # Description
        description_tag = product_soup.find("p", class_="sdesc")
        description = description_tag.text.strip() if description_tag else "No description available."


        # Images
        images = []
        image_section = product_soup.find("div", id="primgms")
        if image_section:
            for img_tag in image_section.find_all("a", href=True):
                images.append(BASE_URL + img_tag["href"])

        # Category
        breadcrumb_div = product_soup.find("div", id="brdc")
        product_category = ""
        if breadcrumb_div:
            breadcrumb_links = breadcrumb_div.find_all("a")
            for link in breadcrumb_links:
                category_name = link.text.strip()
                if category_name and "ΠΡΟΪΟΝΤΑ" not in category_name:  # Ignore unwanted names
                    product_category = category_name  # Keep updating to get the last valid category




        # Characteristics
        characteristics = []
        attributes_section = product_soup.find("div", id="pratr")
        if attributes_section:
            for li in attributes_section.find_all("li"):
                value = li.find("span")
                if value:
                    characteristics.append(value.text.strip())
        characteristics_str = ", ".join(characteristics)
        return {
            "sku": sku,
            "title": title,
            "description": description,
            "images": images,
            "category": product_category,
            "characteristics": characteristics_str,
        }

    except requests.RequestException as e:
        print(f"Error scraping product details for SKU {sku}: {e}")
        return None


def get_category_id_by_name(category_name):
    """
    Fetch the WooCommerce category ID based on the category name.
    :param category_name: The name of the category to fetch.
    :return: The ID of the category if found, otherwise None.
    """
    response = requests.get(
        f"{WP_API_BASE_URL}/categories",
        auth=(WP_API_CONSUMER_KEY, WP_API_CONSUMER_SECRET)
    )

    if response.status_code != 200:
        print(f"Error fetching categories: {response.status_code}, {response.text}")
        return None

    categories = response.json()
    for category in categories:
        if category["name"].lower() == category_name.lower():
            return category["id"]
    print(f"Category '{category_name}' not found.")
    return None


def create_new_product(sku, price):
    """
    Create a new product in WooCommerce by scraping its details from the website.
    :param sku: SKU of the product.
    :param price: The price to set for the product.
    """
    product_details = scrape_product_details(sku)
    if not product_details:
        print(f"Failed to fetch product details for SKU {sku}.")
        return

    # Use the passed-in price instead of the scraped price
    regular_price = str(price) if isinstance(price, (int, float)) else "0.00"

    # Get the category ID
    category_name = product_details["category"].strip()
    category_id = get_category_id_by_name(category_name)
    categories = [{"id": category_id}] if category_id else []

    # Validate and prepare tags and images
    tags = [{"name": char.strip()} for char in product_details["characteristics"].split(",")]
    images = [{"src": img} for img in product_details["images"] if img.startswith("http")]

    # Post the product to WooCommerce
    try:
        payload = {
            "name": product_details["title"],
            "regular_price": regular_price,
            "description": product_details["description"],
            "short_description": product_details["description"][:100],
            "sku": product_details["sku"],
            "categories": categories,
            "images": images,
            "tags": tags,
        }
        print("Payload:", payload)  # Debugging
        post_response = requests.post(
            f"{WP_API_BASE_URL}",
            json=payload,
            auth=(WP_API_CONSUMER_KEY, WP_API_CONSUMER_SECRET),
            timeout=30,
        )
        post_response.raise_for_status()
        print(f"Product with SKU {sku} successfully created with price {regular_price}.")
        return post_response.json()
    except requests.RequestException as e:
        print(f"Error creating product with SKU {sku}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None





#------------------------------------------------------------------------------------------------------------








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








#------------------------------------------------------------------------------------------------------------





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

