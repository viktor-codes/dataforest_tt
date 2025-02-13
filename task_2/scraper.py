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


async def scrape_book(url, browser):
    """Scrapes data from a single book page."""
    try:
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        title_element = await page.query_selector("div.product_main h1")
        title = (
            await title_element.inner_text() if title_element else "No title"
        )

        price_element = await page.query_selector("p.price_color")
        price = (
            await price_element.inner_text() if price_element else "No price"
        )

        rating_element = await page.query_selector("p.star-rating")
        rating_class = (
            await rating_element.get_attribute("class")
            if rating_element
            else ""
        )
        rating = (
            rating_class.replace("star-rating", "").strip()
            if rating_class
            else "No rating"
        )

        stock_element = await page.query_selector("p.instock.availability")
        stock = (
            await stock_element.inner_text()
            if stock_element
            else "No stock info"
        )
        stock = stock.strip()

        image_element = await page.query_selector("div.item.active img")
        image_url = (
            await image_element.get_attribute("src")
            if image_element
            else "No image"
        )
        image_url = urljoin(BASE_URL, image_url)

        description_element = await page.query_selector(
            "#product_description ~ p"
        )
        description = (
            await description_element.inner_text()
            if description_element
            else "No description available"
        )

        category_element = await page.query_selector(
            "ul.breadcrumb li:nth-child(3) a"
        )
        category = (
            await category_element.inner_text()
            if category_element
            else "No category"
        )

        product_info = {}
        rows = await page.query_selector_all("table.table.table-striped tr")
        for row in rows:
            key_element = await row.query_selector("th")
            value_element = await row.query_selector("td")
            key = await key_element.inner_text() if key_element else "Unknown"
            value = (
                await value_element.inner_text()
                if value_element
                else "Unknown"
            )
            product_info[key] = value

        await page.close()
        return {
            "title": title,
            "category": category,
            "price": price,
            "rating": rating,
            "stock": stock,
            "image_url": image_url,
            "description": description,
            "product_information": product_info,
        }
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None


async def get_all_book_links():
    """Scrapes all book links from the website."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(urljoin(BASE_URL, "catalogue/page-1.html"))

        all_book_links = []
        with tqdm(desc="Collecting Links", unit="link") as pbar:
            while True:
                books = await page.query_selector_all(
                    "article.product_pod h3 a"
                )
                for book in books:
                    href = await book.get_attribute("href")
                    full_url = urljoin(page.url, href)
                    all_book_links.append(full_url)
                    pbar.update(1)

                next_button = await page.query_selector("li.next a")
                if not next_button:
                    break

                await page.goto(
                    urljoin(page.url, await next_button.get_attribute("href"))
                )

        await browser.close()
    return all_book_links
