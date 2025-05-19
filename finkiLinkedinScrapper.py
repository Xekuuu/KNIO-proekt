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
#company_logos = {
#    "finki": "https://finki.ukim.mk/sites/default/files/logo_0_0.png",
#    "linkedin": "https://cdn-icons-png.flaticon.com/512/174/174857.png",
#    "it labs": "https://upload.wikimedia.org/wikipedia/commons/3/30/IT_Labs_Logo.png",
#    "netcetera": "https://pbs.twimg.com/profile_images/1095267205065744384/IqFgDL6k_400x400.jpg",
#    "seavus": "https://upload.wikimedia.org/wikipedia/en/f/f4/Seavus_logo.png",
#    "endava": "https://upload.wikimedia.org/wikipedia/en/3/39/Endava_logo.png",
#    "cosmic development": "https://media.licdn.com/dms/image/D4D0BAQF2UJHqVqV3fg/company-logo_200_200/0/1693301162083/cosmic_development_logo?e=2147483647&v=beta&t=m0RCX-Ve8cUBjXjKZtItHOJlKnDcfPlvwRDtfuydPGA",
#}

# Logo test
#def match_logo(name):
#    name = name.lower()
#    for company, logo_url in company_logos.items():
#        if company in name:
#            return logo_url
#    domain_guess = name.replace(" ", "") + ".com"
#    return f"https://logo.clearbit.com/{domain_guess}"

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

    # what the heli 🚁 meine spliff 2.5 exotic 🚁 what the heli 🚁
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
    options.add_argument('--headless') #remove za debug
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url_linkedin)

        time.sleep(5) # 5 ili 7 e ok!

        # multi scroll
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        jobs = soup.select('.base-card') or []
        print(f"Found {len(jobs)} job listings")  # Debugging
        junior_jobs_count = 0

        for job in jobs:
            try:
                # Extract title and link
                title_elem = job.select_one('.base-search-card__title')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = job.select_one('a.base-card__full-link')['href'] if job.select_one(
                    'a.base-card__full-link') else ""

                # IME
                company_elem = job.select_one('.base-search-card__subtitle a')
                company = company_elem.get_text(strip=True) if company_elem else ""


                if not any(keyword in title.lower() for keyword in ['intern', 'junior', 'entry']): #nez drugi keywords koj da klam
                    print(
                        f" Skip: '{title}' @ {company}" if company else f" skip'{title}'")

                    continue
                junior_jobs_count += 1


                # na nekoj raboti na nekoj ne mora segde da bara
                image_url = None
                logo_containers = [
                    job.select_one('.job-search-card__logo img'),  # 1
                    job.select_one('.base-search-card__logo img'),  # 2
                    job.select_one('img.artdeco-entity-image')  # 3
                    #ako ima drug selektor klajgo ovde
                ]

                for img in logo_containers:
                    if img:
                        if img.has_attr('src'):
                            image_url = img['src']
                            break
                        elif img.has_attr('data-delayed-url'):
                            image_url = img['data-delayed-url']
                            break
                        elif img.has_attr('srcset'):
                            srcset = img['srcset'].split(',')
                            if srcset:
                                image_url = srcset[0].split()[0]
                                break



                job_list.append({
                    'title': f"{title} at {company}" if company else title,
                    'link': href,
                    'image': image_url
                })

            except Exception as e:
                print(f"Error processing job: {str(e)}") #debug
                continue
        print(f"  {junior_jobs_count}  najdeni!")  # debug
    except Exception as e:
        print(f"Error in LinkedIn scraping: {str(e)}") #debug
    finally:
        driver.quit()

    return job_list

@app.route("/")
def index():
    jobs = scrape_jobs()
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True)
