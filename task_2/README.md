Here's your **README.md** for the Playwright-based **Books Scraper**, following the same structure and style as your **Vendr Product Scraper**:

---

# **Books Scraper – Playwright & Multiprocessing**

This project is a **high-performance web scraper** designed to collect book information from [Books to Scrape](https://books.toscrape.com/). The scraper efficiently gathers book data using **Python's multiprocessing module** and **Playwright for headless browser automation**.

### **Features**
- **Asynchronous & Multiprocessing Scraping** – Scrapes multiple book pages in parallel for speed.
- **Pagination Support** – Collects book links dynamically across multiple pages.
- **Full Product Data Extraction** – Extracts **title, category, price, rating, stock availability, image URL, description, and detailed product info**.
- **TQDM Progress Bars** – Displays real-time progress while scraping.
- **Rotating Log Files** – Stores logs efficiently in `logs/scraper.log`.
---

## **📂 Project Structure**
```
dataforest_tt/
├── task_2/
│   └── books_data.json      # JSON file with scraped book data
│   ├── logs/
│   │   └── scraper.log          # Rotating log file for scraping activity
│   ├── .env.example             # Sample environment file
│   ├── requirements.txt         # Project dependencies
│   ├── scraper.py               # Main scraping script
│   └── README.md
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

---

## **Getting Started**

### **1.Clone the Repository**
```bash
git clone https://github.com/viktor-codes/dataforest_tt.git
cd dataforest_tt/task_2
```

---

### **2.Create a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

### **3.Install Dependencies**
```bash
pip install -r requirements.txt
```

Additionally, install Playwright’s Chromium browser:
```bash
playwright install
```

---

### **4.Configure Environment Variables**
Copy the `.env.example` file and modify it if needed:
```bash
cp .env.example .env
```

**Available Configuration Variables:**
```
BASE_URL=https://books.toscrape.com/
OUTPUT_FILE=data/books_data.json
```

---

### **5.Run the Scraper**
```bash
python scraper.py
```

---

## **How It Works**
1. **Collects all book links** – Scrapes every book link dynamically from the website.
2. **Launches multiple processes** – Divides the workload into chunks to speed up scraping.
3. **Scrapes book details** – Extracts **title, category, price, rating, stock availability, image URL, description, and product information**.
4. **Stores data in JSON** – Saves the scraped book data into `books_data.json`.

---

## **Logging & Debugging**
- **All logs are stored in** `logs/scraper.log`
- **Rotating logs prevent large log files**
- **No logs are displayed in the console** (only saved in the file)

To **monitor logs in real-time**, open another terminal and use:
```bash
tail -f logs/scraper.log
```

---

## **Dependencies**
The project uses the following **Python libraries**:

| Package           | Purpose |
|------------------|---------|
| `playwright`      | Browser automation for scraping |
| `asyncio`        | Asynchronous processing |
| `tqdm`           | Progress bars |
| `python-dotenv`  | Manage environment variables |
| `multiprocessing` | Parallel processing for speed |
| `logging`        | Log management |

**Install all dependencies with:**
```bash
pip install -r requirements.txt
```

## **Example Output**
Example **JSON file (`books_data.json`)** with collected data:
```json
[
    {
        "title": "The Catcher in the Rye",
        "category": "Fiction",
        "price": "£39.95",
        "rating": "Four",
        "stock": "In stock (23 available)",
        "image_url": "https://books.toscrape.com/.../image.jpg",
        "description": "A classic novel...",
        "product_information": {
            "UPC": "123456789",
            "Product Type": "Books",
            "Tax": "£0.00",
            "Availability": "23 available"
        }
    }
]
```
