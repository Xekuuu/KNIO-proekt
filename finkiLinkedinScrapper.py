import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time





        title = tag.get_text(strip=True)

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    time.sleep(5)

    driver.quit()


    for job in jobs:
            if any(keyword in title.lower() for keyword in ['intern', 'junior', 'entry']):
