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
