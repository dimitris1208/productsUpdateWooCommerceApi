# WooCommerce Product Updater

This project automates the synchronization of products between an external website (`your_website`) and your WooCommerce store. It handles the following functionalities:

1. **Scrape Product Details**: Fetch product SKUs, prices, and other necessary details from the external website.
2. **Fetch WooCommerce Products**: Retrieve products from the WooCommerce store using the REST API.
3. **Compare Products**: Compare products between the two sources, update prices, add new products, and delete unmatched ones.
4. **Handle Duplicates**: Removes duplicates from CSV files based on the SKU column.

## File Structure

- **`fetch_website.py`**: Scrapes SKUs and prices from `your_website` categories.
- **`fetch_woo.py`**: Fetches SKUs and prices of products in WooCommerce via the REST API.
- **`compare.py`**: Compares products from `your_website` and WooCommerce, updates prices, flags matched products, and deletes unmatched ones.
- **`update_api.py`**: Contains functions to:
  - Update product prices.
  - Delete products.
  - Create new products by scraping detailed information from the website.
- **`category_urls.py`**: A list of URLs for the website categories to scrape.



### Environment File
Create a `.env` file in the root directory with the following variables:
WP_API_BASE_URL=your_woocommerce_api_url WP_API_CONSUMER_KEY=your_woocommerce_consumer_key WP_API_CONSUMER_SECRET=your_woocommerce_consumer_secret



Replace `your_woocommerce_api_url` with your WooCommerce API base URL (e.g., `https://yourwebsite.com/wp-json/wc/v3/products`), and provide your API keys.

### Dependencies
Install the required Python libraries:
pip install requests pandas beautifulsoup4 python-dotenv



## Usage

### 1. Fetch Website Products
Run `fetch_website.py` to scrape SKUs and prices from the external website.
python fetch_website.py


Output: `website_products.csv`.

### 2. Fetch WooCommerce Products
Run `fetch_woo.py` to fetch SKUs and prices from WooCommerce.
python fetch_woo.py


Output: `woocommerce_products.csv`.

### 3. Compare and Sync Products
Run `compare.py` to compare products, update prices, add new products, and delete unmatched ones.
python compare.py


### 4. Remove Duplicates
Both `fetch_website.py` and `fetch_woo.py` include a `remove_duplicates()` function to clean the CSV files.

## Customization
Modify the `BASE_URL` in `fetch_website.py` and scraping logic as needed to match the structure of your website. Replace `your_website` with the actual website name.

## Notes
- Ensure proper credentials are set in the `.env` file.
- This project is tailored for a specific website structure. Adjust scraping logic for other sites.
- Backup your WooCommerce store before running scripts that update or delete products.
