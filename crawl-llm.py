import os
import json
import asyncio
import csv
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Set
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai import RateLimiter, CrawlerMonitor, DisplayMode

load_dotenv()

CSV_FILE = "scraped-data/job_contacts.csv"

# ---------- Data Model ----------

class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the contact person")
    title: Optional[str] = Field(None, description="Job title of the contact person")
    email: Optional[str] = Field(None, description="Email address of the contact person")
    phone: Optional[str] = Field(None, description="Phone number of the contact person")

# ---------- CSV Handler Module ----------

class CSVHandler:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file

    def load_existing_leads(self) -> Set[str]:
        existing_leads = set()
        if os.path.exists(self.csv_file):
            with open(self.csv_file, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_leads.add(row["detail_url"])
        return existing_leads

    def append_new_leads(self, new_leads: List[dict]):
        fieldnames = [
            "detail_url", "job_title", "company", "location",
            "contact_name1", "contact_title1", "contact_email1", "contact_phone1",
            "contact_name2", "contact_title2", "contact_email2", "contact_phone2"
        ]
        file_exists = os.path.exists(self.csv_file) and os.stat(self.csv_file).st_size > 0
        with open(self.csv_file, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_leads)

# ---------- Crawler Service Module ----------

class JobCrawler:
    def __init__(self):
        self.browser_cfg = BrowserConfig(headless=True)
        self.llm_strategy = LLMExtractionStrategy(
            provider="openai/gpt-4o-mini",
            api_token=os.getenv("OPENAI_API_KEY"),
            schema=ContactInfo.model_json_schema(),
            extraction_type="schema",
            instruction=("Extract ONLY contact person data from the job ad, including their name, "
                         "title, email, and phone number as a JSON array. DO NOT ADD JOHN DOE, JANE SMITH "
                         "or any other non-existent data. If no data is present, leave empty. Ignore ALL OTHER information."),
            chunk_token_threshold=1200,
            overlap_rate=0.1,
            apply_chunking=True,
            input_format="markdown",
            extra_args={"temperature": 0.1, "max_tokens": 1000},
            verbose=True,
        )
        self.crawl_config = CrawlerRunConfig(
            extraction_strategy=self.llm_strategy,
            cache_mode=CacheMode.BYPASS
        )
        self.dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=80.0,
            check_interval=1.0,
            max_session_permit=10,
            rate_limiter=RateLimiter(
                base_delay=(1.0, 2.0),
                max_delay=30.0,
                max_retries=3,
                rate_limit_codes=[429, 503]
            ),
            monitor=CrawlerMonitor(
                max_visible_rows=15,
                display_mode=DisplayMode.DETAILED
            )
        )

    async def crawl(self, urls: List[str]):
        async with AsyncWebCrawler(config=self.browser_cfg) as crawler:
            results = await crawler.arun_many(
                urls=urls,
                config=self.crawl_config,
                dispatcher=self.dispatcher
            )
        return results

    def process_results(self, results, url_to_job_mapping: dict) -> List[dict]:
        new_job_details = []
        for result in results:
            if result.success:
                contacts = json.loads(result.extracted_content)
                job = url_to_job_mapping.get(result.url)
                if job:
                    contact1 = contacts[0] if len(contacts) > 0 else {}
                    contact2 = contacts[1] if len(contacts) > 1 else {}
                    new_job_details.append({
                        "detail_url": job["detail_url"],
                        "job_title": job.get("job_title", "Unknown Title"),
                        "company": job.get("company", "Unknown Company"),
                        "location": job.get("location", "Unknown Location"),
                        "contact_name1": contact1.get("name", ""),
                        "contact_title1": contact1.get("title", ""),
                        "contact_email1": contact1.get("email", ""),
                        "contact_phone1": contact1.get("phone", ""),
                        "contact_name2": contact2.get("name", ""),
                        "contact_title2": contact2.get("title", ""),
                        "contact_email2": contact2.get("email", ""),
                        "contact_phone2": contact2.get("phone", ""),
                    })
            else:
                print(f"Error extracting from {result.url}: {result.error_message}")
        return new_job_details

# ---------- Main Logic ----------

async def extract_job_contacts(jobs):
    csv_handler = CSVHandler(CSV_FILE)
    existing_leads = csv_handler.load_existing_leads()

    # Filter out jobs that have been processed already.
    url_to_job_mapping = {job["detail_url"]: job for job in jobs if job["detail_url"] not in existing_leads}
    if not url_to_job_mapping:
        print("No new job ads found. Skipping scraping.")
        return []

    urls = list(url_to_job_mapping.keys())
    job_crawler = JobCrawler()
    results = await job_crawler.crawl(urls)
    return job_crawler.process_results(results, url_to_job_mapping)

async def main():
    with open("scraped-data/job_urls.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    new_job_details = await extract_job_contacts(jobs)
    if not new_job_details:
        print("No new job ads to append. Exiting.")
        return

    csv_handler = CSVHandler(CSV_FILE)
    csv_handler.append_new_leads(new_job_details)
    print(f"Added {len(new_job_details)} new job listings to {CSV_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
