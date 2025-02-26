import json
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def extract_job_urls():
    base_url = "https://www.it-jobbank.dk/jobsoegning"
    all_jobs = []
    next_page_url = base_url

    async with AsyncWebCrawler(verbose=True) as crawler:
        while next_page_url:
            schema = {
                "name": "Job Ads Extraction",
                "baseSelector": "div.jobsearch-result",
                "fields": [
                    {
                        "name": "detail_url",
                        "selector": "a[href*='/jobannonce/']",
                        "type": "attribute",
                        "attribute": "href"
                    },
                    {
                        "name": "job_title",
                        "selector": ".job-title",
                        "type": "text"
                    },
                    {
                        "name": "company",
                        "selector": ".job-company",
                        "type": "text"
                    },
                    {
                        "name": "location",
                        "selector": ".job-location",
                        "type": "text"
                    }
                ]
            }
            strategy = JsonCssExtractionStrategy(schema, verbose=True)
            config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy)

            result = await crawler.arun(url=next_page_url, config=config)
            if not result.success:
                print(f"Failed to fetch {next_page_url}: {result.error_message}")
                break

            page_data = json.loads(result.extracted_content)
            all_jobs.extend(page_data)

            # Extract next page URL
            next_page_result = await crawler.arun(
                url=next_page_url,
                config=CrawlerRunConfig(
                    extraction_strategy=JsonCssExtractionStrategy(
                        {
                            "name": "Pagination Extraction",
                            "baseSelector": "li.page-item.page-item-next",
                            "fields": [
                                {
                                    "name": "next_page",
                                    "selector": "a",
                                    "type": "attribute",
                                    "attribute": "href"
                                }
                            ]
                        }
                    ),
                    cache_mode=CacheMode.BYPASS
                )
            )

            if next_page_result.success:
                next_page_data = json.loads(next_page_result.extracted_content)
                next_page_url = next_page_data[0]["next_page"] if next_page_data else None
            else:
                next_page_url = None

    return all_jobs

async def main():
    jobs = await extract_job_urls()

    # Convert relative URLs to absolute and clean up text
    for job in jobs:
        if job.get("detail_url", "").startswith("/"):
            job["detail_url"] = "https://www.it-jobbank.dk" + job["detail_url"]
        if "company" in job:
            job["company"] = job["company"].strip()
        if "job_title" in job:
            job["job_title"] = job["job_title"].strip()
        if "location" in job:
            job["location"] = job["location"].strip()

    with open("job_urls.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(jobs)} job listings across multiple pages.")

asyncio.run(main())
