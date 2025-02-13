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
