import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


# finki stranata za praksa

URL_COLLEGE = "https://finki.ukim.mk/mk/jobs-and-internships"
BASE_COLLEGE = "https://finki.ukim.mk"

response = requests.get(URL_COLLEGE)
soup_college = BeautifulSoup(response.text, 'html.parser')
results_college = soup_college.select('span.field-content > a')

print("FINKI Jobs/Internships:")
for tag in results_college:
    title = tag.get_text(strip=True)
    href = BASE_COLLEGE + tag['href']
    print(f"- {title} ({href})")

# finki stranata za praksa end

# linkedin scrapper 😎

URL_LINKEDIN = "https://mk.linkedin.com/jobs/junior-programmer-jobs?countryRedirected=1"

# Start Selenium browser
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # izbrisi za testing
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get(URL_LINKEDIN)
time.sleep(5)

soup_linkedin = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

print("\nLinkedIn Junior/Intern Jobs:")
jobs = soup_linkedin.select('a.base-card__full-link')

for job in jobs:
    title = job.get_text(strip=True)
    href = job['href']
    if any(keyword in title.lower() for keyword in ['intern', 'junior', 'entry']):
        print(f"- {title} ({href})")
