import requests
import queue
import sqlite3
import time
import logging
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://www.vendr.com")
DB_FILE = os.getenv("DB_FILE", "products.db")
CATEGORIES = ["DevOps", "IT Infrastructure", "Data Analytics & Management"]

# Configure Logging with RotatingFileHandler
log_file = "logs/scraper.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3
        ),  # 5MB per file, 3 backups
        logging.StreamHandler(),
    ],
)

# Initialize Queues
product_queue = queue.Queue()
db_queue = queue.Queue()

# Stop signal for threads
STOP_SIGNAL = None


# Database Setup
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            description TEXT,
            price_range TEXT,
            median_price TEXT
        )
    """
    )
    conn.commit()
    conn.close()


# Retry Decorator for Network Requests
def retry(max_attempts=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    logging.warning(
                        f"Request failed: {e}. "
                        f"Retrying {attempts + 1}/{max_attempts}..."
                    )
                    attempts += 1
                    time.sleep(delay)
            logging.error(f"Failed after {max_attempts} attempts.")
            return None

        return wrapper

    return decorator


# Fetch Page Content with Retry
@retry()
def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


# Utility function to handle URL construction
def construct_full_url(href):
    return BASE_URL + href if href.startswith("/") else href


# Get Category URLs
def get_category_urls():
    home_page_content = fetch_page(BASE_URL)
    if not home_page_content:
        logging.error("Failed to load homepage.")
        return []

    soup = BeautifulSoup(home_page_content, "lxml")
    category_links = []

    for link in soup.find_all(
        "a", class_="rt-Text rt-reset rt-Link rt-underline-auto"
    ):
        category_name = link.text.strip()
        if category_name in CATEGORIES:
            full_url = construct_full_url(link["href"])
            category_links.append((category_name, full_url))

    return category_links


# Get Products from Subcategories with Pagination
def get_products_from_subcategory(subcategory_url, subcategory_name):
    products = []
    page = 1

    while True:
        paginated_url = (
            f"{subcategory_url.split('?')[0]}?verified=false&page={page}"
        )
        subcategory_content = fetch_page(paginated_url)

        if not subcategory_content:
            logging.warning(
                f"Failed to load subcategory page {page}: {paginated_url}"
            )
            break

        soup = BeautifulSoup(subcategory_content, "lxml")
        product_cards = soup.find_all("a", class_="_card_j928a_9")

        if not product_cards:
            logging.info(
                f"No more products found on page {page}. Ending pagination."
            )
            break

        for product in product_cards:
            name = product.find(
                "span", class_="_cardTitle_j928a_13"
            ).text.strip()
            description = product.find(
                "span", class_="_description_j928a_18"
            ).text.strip()
            product_url = construct_full_url(product["href"])

            products.append(
                {
                    "name": name,
                    "category": subcategory_name,
                    "description": description,
                    "url": product_url,
                }
            )

        logging.info(f"Scraped page {page} of: {subcategory_name}")
        page += 1

    return products


# Extract Price Data
def extract_price_data(product_url):
    content = fetch_page(product_url)
    if not content:
        logging.warning(f"Failed to load product page: {product_url}")
        return {"price_range": "N/A", "median_price": "N/A"}

    soup = BeautifulSoup(content, "lxml")
    price_range_elem = soup.find("span", {"data-accent-color": "green"})
    median_value_elem = soup.find("span", class_="v-fw-700 v-fs-24")

    price_range = price_range_elem.text.strip() if price_range_elem else "N/A"
    median_price = (
        median_value_elem.text.strip() if median_value_elem else "N/A"
    )

    return {"price_range": price_range, "median_price": median_price}
