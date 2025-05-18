import requests
from bs4 import BeautifulSoup

URL = "https://finki.ukim.mk/mk/jobs-and-internships"
BASE = "https://finki.ukim.mk"

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

#<span class="field-content">
results = soup.select('span.field-content > a')

print("names:")
for tag in results:
    title = tag.get_text(strip=True)
    href = BASE + tag['href']
    print(f"- {title} ({href})")
