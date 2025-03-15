# **Job Crawler using `crawl4ai`**

## **Overview**
This project is a web scraping pipeline that extracts job listings and contact details from **IT Job Bank** using `crawl4ai`. It consists of two main scripts:

1. **`crawl.py`** – Scrapes job listings and saves them in `scraped-data/job_urls.json`.
2. **`crawl-llm.py`** – Extracts contact information from job ads using an LLM (GPT-4o-mini) and saves results in `scraped-data/job_contacts.csv`.

## **Features**
- **Automated job listing extraction** – Scrapes job details like title, company, and location.
- **Pagination handling** – Crawls multiple pages dynamically.
- **Contact information extraction** – Uses `crawl4ai` and GPT-4o-mini to extract recruiter details.
- **CSV output** – Saves extracted job contacts in a structured format.

## **Setup & Installation**

### **1. Clone the repository**
```sh
git clone <your-repo-url>
cd <your-repo-name>
```

### **2. Install dependencies (Recommended: `uv`)**
I **highly recommend using `uv`** for package management due to its speed and efficiency. To install dependencies, run:
```sh
uv pip install -r requirements.txt
```
Alternatively, you can use `pip`:
```sh
pip install -r requirements.txt
```

### **3. Install `crawl4ai`**
After installing the dependencies, install `crawl4ai`:
```sh
pip install crawl4ai
```

### **4. Run `crawl4ai` setup**
Initialize `crawl4ai` by running:
```sh
crawl4ai-setup
```
This command will:
- Install or update required Playwright browsers (Chromium, Firefox, etc.).
- Perform OS-level checks (e.g., missing libraries on Linux).
- Confirm your environment is ready to crawl.

### **5. Verify the installation**
Optionally, run diagnostics to confirm everything is functioning:
```sh
crawl4ai-doctor
```
This command will:
- Check Python version compatibility.
- Verify Playwright installation.
- Inspect environment variables or library conflicts.

If any issues arise, follow the suggestions provided and re-run `crawl4ai-setup`.

### **6. Set up environment variables**
Create a `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## **Usage**
I also use `uv` to run the scripts for faster execution:

1. **Run the job crawler to collect job listings**
   ```sh
   uv python crawl.py
   ```
2. **Extract contact details from job ads**
   ```sh
   uv python crawl-llm.py
   ```

## **Output Files**
- `scraped-data/job_urls.json` – Stores scraped job listings.
- `scraped-data/job_contacts.csv` – Stores extracted recruiter contact details.

## **Dependencies**
- `crawl4ai` (Web crawling and LLM-based extraction)
- `pydantic` (Data validation)
- `python-dotenv` (Environment variable management)
- `asyncio` (Asynchronous execution)

## **Future Enhancements**
- Improve error handling and retry mechanisms.
- Add more job boards for broader coverage.
- Implement a UI or API for querying job contacts.