from lxml import html

# Load the HTML content
with open('it-jobbank.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML
tree = html.fromstring(html_content)

# Define XPath patterns for the data fields
job_titles = tree.xpath('//h2[contains(@class, "job-title")]/text()')
company_names = tree.xpath('//div[contains(@class, "company-name")]/text()')
locations = tree.xpath('//div[contains(@class, "job-location")]/text()')

# Extract and print the data
for title, company, location in zip(job_titles, company_names, locations):
    print(f"Job Title: {title}")
    print(f"Company: {company}")
    print(f"Location: {location}")
    print("------")