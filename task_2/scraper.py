from urllib.parse import urljoin
from playwright.async_api import async_playwright
from tqdm import tqdm
import logging
import os
from dotenv import load_dotenv
from multiprocessing import set_start_method
from logging.handlers import RotatingFileHandler

# Required for macOS multiprocessing
set_start_method("spawn", force=True)

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://books.toscrape.com/")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "books_data.json")

# Configure Logging with RotatingFileHandler
log_file = "logs/scraper.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3),
    ],
)

async def get_all_book_links():
    """Scrapes all book links from the website."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(urljoin(BASE_URL, "catalogue/page-1.html"))

        all_book_links = []
        with tqdm(desc="Collecting Links", unit="link") as pbar:
            while True:
                books = await page.query_selector_all("article.product_pod h3 a")
                for book in books:
                    href = await book.get_attribute("href")
                    full_url = urljoin(page.url, href)
                    all_book_links.append(full_url)
                    pbar.update(1)

                next_button = await page.query_selector("li.next a")
                if not next_button:
                    break

                await page.goto(urljoin(page.url, await next_button.get_attribute("href")))

        await browser.close()
    return all_book_links
