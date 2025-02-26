import json
import asyncio
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonXPathExtractionStrategy

# Regular expressions for extracting phone numbers, emails, and names
PHONE_REGEX = r'\b\d{2,4}[\s-]?\d{2,4}[\s-]?\d{2,4}\b'
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
NAME_TITLE_REGEX = r'(\b[A-ZÆØÅa-zæøå]+\s[A-ZÆØÅa-zæøå]+)(?:\s*[-|–]\s*(\w+))?'

async def extract_job_contact_details(url):
    if url.startswith("/"):
        url = "https://www.it-jobbank.dk" + url

    schema = {
        "name": "Job Ad Contact Extraction",
        "baseSelector": "//*",
        "fields": [
            {
                "name": "ad_html",
                "selector": "//*[@id='job_ad']",
                "type": "html"
            }
        ]
    }
    strategy = JsonXPathExtractionStrategy(schema, verbose=True)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy)
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            print(f"Detail crawl failed for {url}: {result.error_message}")
            return None

        data = json.loads(result.extracted_content)
        ad_html = data[0].get("ad_html", "") if isinstance(data, list) and data else ""

        # Extract phone numbers and emails using regex
        phone_numbers = re.findall(PHONE_REGEX, ad_html)
        emails = re.findall(EMAIL_REGEX, ad_html)

        # Extract name and title using regex (assuming they are present near the email/phone)
        contact_details = []
        for email in emails:
            match = re.search(NAME_TITLE_REGEX, ad_html)
            if match:
                name = match.group(1)
                title = match.group(2) if match.group(2) else "Unknown Title"
                contact_details.append({
                    "email": email,
                    "name": name,
                    "title": title
                })

        # Return the extracted contact details
        return {
            "url": url,
            "contact_details": contact_details,
            "phone_numbers": phone_numbers
        }

async def main():
    with open("job_urls.json", "r", encoding="utf-8") as f:
        urls = json.load(f)

    tasks = [asyncio.create_task(extract_job_contact_details(item.get("detail_url")))
             for item in urls if item.get("detail_url")]

    details = await asyncio.gather(*tasks)

    with open("job_contacts_with_names.json", "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2)

    print("Job contacts with names and titles saved to job_contacts_with_names.json")

asyncio.run(main())
