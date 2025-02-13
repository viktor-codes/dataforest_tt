# Vendr Product Scraper

This project is a **multi-threaded web scraper** designed to collect product information from [Vendr](https://www.vendr.com/). The scraper focuses on three categories:

- **DevOps**
- **IT Infrastructure**
- **Data Analytics & Management**

Collected data includes **product names, categories, descriptions, price ranges, and median prices**. The results are stored in an **SQLite database**.

---

## Features

- **Multi-threaded scraping** for faster data collection using Python's `threading` and `queue` modules.
- **Retry logic** for robust handling of network errors.
- **Pagination support** to scrape products across multiple pages.
- **Rotating log files** for efficient logging and debugging.
- **Environment variable management** with `.env` for flexible configurations.
- **SQLite database integration** to store and manage scraped data.

---

## Project Structure

```
dataforest_tt/                 
├── task_1/
│   ├── data/
│   │   └── products.db        # SQLite database (auto-created)
│   ├── logs/
│   │   └── scraper.log        # Rotating log file for scraping activity
│   ├── .env.example           # Sample environment file
│   ├── requirements.txt       # Project dependencies
│   └── scraper.py             # Main scraping script
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

---

## Getting Started

### **1. Clone the Repository**

```bash
git clone https://github.com/viktor-codes/dataforest_tt.git
cd dataforest_tt/task_1
```

---

### **2. Create a Virtual Environment**

It's recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

---

### **4. Configure Environment Variables**

Copy the sample `.env.example` file and modify it if needed:

```bash
cp .env.example .env
```

### **5. Run the Scraper**

```bash
python scraper.py
```

---

## How It Works

1. **Initialize Database:**  
   The scraper creates an SQLite database (`products.db`) if it doesn't exist.

2. **Fetch Categories and Subcategories:**  
   It scrapes product links from the specified categories and handles pagination.

3. **Multithreaded Scraping:**  
   - Multiple threads fetch product details concurrently.
   - A dedicated thread writes the data to the database.

4. **Logging:**  
   All scraping activities and errors are logged in `logs/scraper.log`.

---

## Dependencies

The project uses the following Python libraries:

- **`requests`** - For HTTP requests.
- **`beautifulsoup4`** - For parsing HTML content.
- **`tqdm`** - For progress bars.
- **`python-dotenv`** - For managing environment variables.
- **`sqlite3`** - For storing data in a local database.

**Install all dependencies with:**

```bash
pip install -r requirements.txt
```

---

## Logs and Debugging

Logs are stored in `logs/scraper.log` and managed using **rotating log files**. This prevents log files from growing too large.

You can monitor the scraping process in real-time in the console or check the log file for detailed information.

---

## Customization

- **Categories:**  
  To scrape additional categories, update the `CATEGORIES` list in `scraper.py`:

  ```python
  CATEGORIES = ["DevOps", "IT Infrastructure", "Data Analytics & Management"]
  ```

- **Database Location:**  
  You can change the database file path by modifying `DB_FILE` in the `.env` file.