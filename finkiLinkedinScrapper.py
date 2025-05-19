from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# testiranje gluposti
company_logos = {
    "finki": "https://finki.ukim.mk/sites/default/files/logo_0_0.png",
    "linkedin": "https://cdn-icons-png.flaticon.com/512/174/174857.png",
    "it labs": "https://upload.wikimedia.org/wikipedia/commons/3/30/IT_Labs_Logo.png",
    "netcetera": "https://pbs.twimg.com/profile_images/1095267205065744384/IqFgDL6k_400x400.jpg",
    "seavus": "https://upload.wikimedia.org/wikipedia/en/f/f4/Seavus_logo.png",
    "endava": "https://upload.wikimedia.org/wikipedia/en/3/39/Endava_logo.png",
    "cosmic development": "https://media.licdn.com/dms/image/D4D0BAQF2UJHqVqV3fg/company-logo_200_200/0/1693301162083/cosmic_development_logo?e=2147483647&v=beta&t=m0RCX-Ve8cUBjXjKZtItHOJlKnDcfPlvwRDtfuydPGA",
}

# Logo test
def match_logo(name):
    name = name.lower()
    for company, logo_url in company_logos.items():
        if company in name:
            return logo_url
    domain_guess = name.replace(" ", "") + ".com"
    return f"https://logo.clearbit.com/{domain_guess}"

# Scraper
def scrape_jobs():
    job_list = []

    # FINKI
    url_college = "https://finki.ukim.mk/mk/jobs-and-internships"
    base_college = "https://finki.ukim.mk"
    response = requests.get(url_college)
    soup = BeautifulSoup(response.text, 'html.parser')

    # ime + link
    title_tags = soup.select('span.field-content > a')

    # logo
    image_tags = soup.select('div.field-content img')

    # what the heli 🚁 meine spliff 2.5 exotic 🚁
    for title_tag, image_tag in zip(title_tags, image_tags):
        title = title_tag.get_text(strip=True)
        href = base_college + title_tag['href']

        image_url = image_tag.get('src')
        if image_url.startswith('/'):
            image_url = base_college + image_url

        job_list.append({
            'title': title,
            'link': href,
            'image': image_url
        })

    # LinkedIn
    url_linkedin = "https://mk.linkedin.com/jobs/junior-programmer-jobs?countryRedirected=1"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') #<--- izbrisi za debugging
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url_linkedin)
    time.sleep(5) # klaj na poke ako kajvas ne loadnuva/nema rezultati

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    jobs = soup.select('.base-card')

    for job in jobs:
        title_elem = job.select_one('.base-card__full-link')
        company_elem = job.select_one('.base-search-card__subtitle')

        if title_elem:
            title = title_elem.get_text(strip=True)
            href = title_elem['href']
            company = company_elem.get_text(strip=True) if company_elem else ""

            if any(keyword in title.lower() for keyword in ['intern', 'junior', 'entry']): #nez drugi keywords za praksa
                logo = match_logo(company or title)
                job_list.append({
                    'title': f"{title} at {company}" if company else title,
                    'link': href,
                    'image': logo
                })

    return job_list

@app.route("/")
def index():
    jobs = scrape_jobs()
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True)
