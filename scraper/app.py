from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

# ------------------- BROWSER -------------------

def get_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ------------------- SCRAPERS -------------------

def scrape_infopark(driver):
    jobs = []
    driver.get("https://infopark.in/companies/job-search")
    time.sleep(5)

    cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job/']")
    for c in cards:
        title = c.text.strip()
        link = c.get_attribute("href")
        if title:
            jobs.append({"title": title, "company": "Infopark", "link": link})

    return jobs

def scrape_technopark(driver):
    jobs = []
    driver.get("https://technopark.in/job-search")
    time.sleep(5)

    cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job/']")
    for c in cards:
        title = c.text.strip()
        link = c.get_attribute("href")
        if title:
            jobs.append({"title": title, "company": "Technopark", "link": link})

    return jobs

def scrape_cyberpark(driver):
    jobs = []
    driver.get("https://www.ulcyberpark.com/jobs")
    time.sleep(4)

    cards = driver.find_elements(By.TAG_NAME, "a")
    for c in cards:
        title = c.text.strip()
        link = c.get_attribute("href")
        if title and "job" in title.lower():
            jobs.append({"title": title, "company": "Cyberpark", "link": link})

    return jobs

# ------------------- MAIL -------------------

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    body = ""

    if not jobs:
        body = "No jobs found today."
    else:
        for j in jobs[:40]:
            body += f"{j['title']}\n{j['company']}\n{j['link']}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Mail sent with", len(jobs), "jobs.")

# ------------------- MAIN -------------------

if __name__ == "__main__":
    driver = get_browser()

    jobs = []
    jobs += scrape_infopark(driver)
    jobs += scrape_technopark(driver)
    jobs += scrape_cyberpark(driver)

    driver.quit()

    print("Total jobs collected:", len(jobs))
    send_email(jobs)
