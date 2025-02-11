import os
from dotenv import load_dotenv
import sqlite3


# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://www.vendr.com")
DB_FILE = os.getenv("DB_FILE", "products.db")
CATEGORIES = ["DevOps", "IT Infrastructure", "Data Analytics & Management"]


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
