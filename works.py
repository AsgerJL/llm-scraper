import asyncio
import json
import re
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

EMAIL_REGEX = r'[\w\.-]+@[\w\.-]+\.\w+'
PHONE_REGEX = r'\b\d{4}\s+\d{4}\b'

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

async def test_scrape():
    # Hardcoded URL for testing:
    detail_url = "https://www.it-jobbank.dk/jobannonce/h1540205/talstaerk-studentermedhjaelper-med-interesse-for-styring-og-ledelsesinformation-paa-udlaendinge-og-integrationsomraadet"

    schema = {
        "name": "Job Ad Detail Extraction",
        "baseSelector": "#job_ad",
        "fields": [
            {
                "name": "ad_html",
                "selector": "#job_ad",
                "type": "html"
            }
        ]
    }
    strategy = JsonCssExtractionStrategy(schema, verbose=True)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy)

    async with AsyncWebCrawler(verbose=True) as crawler:
        # Crawl the job detail page:
        result = await crawler.arun(url=detail_url, config=config)

        # Print out the raw HTML:
        print("======= RAW HTML START =======")
        print(result.response_text)
        print("======== RAW HTML END ========")

        if not result.success:
            print(f"Detail crawl failed for {detail_url}: {result.error_message}")
            return

        # Extract the portion of HTML under #job_ad:
        data = json.loads(result.extracted_content)
        ad_html = data[0].get("ad_html", "") if isinstance(data, list) and data else ""
        ad_text = html_to_text(ad_html)

        # Find emails & phones:
        emails = re.findall(EMAIL_REGEX, ad_text)
        phones = re.findall(PHONE_REGEX, ad_text)

        print("Emails found:", emails)
        print("Phones found:", phones)

if __name__ == "__main__":
    asyncio.run(test_scrape())
