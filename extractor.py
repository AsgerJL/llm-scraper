import requests

url = 'https://www.it-jobbank.dk/jobsoegning'
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    with open('job-overview.html', 'w', encoding='utf-8') as file:
        file.write(html)
    print("HTML has been saved to output.html")
else:
    print(f"Failed to retrieve content: {response.status_code}")
