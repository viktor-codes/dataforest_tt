import asyncio
import json
import time
import logging
import math
from dotenv import load_dotenv
import os
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from multiprocessing import Process, set_start_method, Manager
from logging.handlers import RotatingFileHandler
from tqdm import tqdm

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

# Stop signal for multiprocessing queues
STOP_SIGNAL = "STOP"


# Class to Manage Processes
class ProcessManager:
    def __init__(self, num_processes, book_links):
        self.num_processes = num_processes
        self.book_links = book_links
        self.manager = Manager()
        self.queue = self.manager.Queue()
        self.processes = []
        self.link_chunks = self._split_links()

    def _split_links(self):
        """Splits book links into chunks for each process."""
        chunk_size = math.ceil(len(self.book_links) / self.num_processes)
        return [
            self.book_links[i * chunk_size: (i + 1) * chunk_size]
            for i in range(self.num_processes)
        ]

    def start_processes(self):
        """Starts the scraping processes."""
        for i, chunk in enumerate(self.link_chunks):
            process = Process(
                target=scraper_worker, args=(chunk, self.queue, len(chunk))
            )
            self.processes.append(process)
            process.start()
            logging.info(f"Process {process.pid} started!")

    def collect_data(self):
        """Collects scraped data from all processes."""
        all_data = []
        stop_signals = 0

        while stop_signals < self.num_processes:
            result = self.queue.get()
            if result == STOP_SIGNAL:
                stop_signals += 1
            else:
                all_data.extend(result)

        return all_data

    def run(self):
        """Starts, monitors, and collects scraping results."""
        self.start_processes()

        # Wait for all processes to complete
        for process in self.processes:
            process.join()

        results = self.collect_data()

        # Force terminate any hanging processes
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                logging.warning(
                    f"Process {process.pid} was forcibly terminated."
                )

        return results


def scraper_worker(link_chunk, queue, total_links):
    """Process worker function."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(scrape_books(link_chunk, total_links))
    queue.put(results)
    queue.put(STOP_SIGNAL)


async def scrape_books(links, total_links):
    """Scrapes multiple book pages using Playwright."""
    data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        with tqdm(
            total=total_links, desc="📖 Scraping Books", unit="book"
        ) as pbar:
            for link in links:
                book_data = await scrape_book(link, browser)
                if book_data:
                    data.append(book_data)
                pbar.update(1)
        await browser.close()
    return data


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

        logging.info(f"Scraped Book: {title}.")

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


# Main Execution
if __name__ == "__main__":
    logging.info("Collecting book links...")
    start_time = time.perf_counter()
    book_links = asyncio.run(get_all_book_links())

    logging.info("Starting multiprocessing scraper...")
    manager = ProcessManager(num_processes=3, book_links=book_links)
    scraped_data = manager.run()

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)

    total_time = time.perf_counter() - start_time
    logging.info(
        f"Scraping completed successfully in {total_time: .2f} seconds!"
    )
