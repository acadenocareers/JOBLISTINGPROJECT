import time
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ===================== ENV =====================

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

# ===================== SELENIUM SETUP =====================

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# ===================== CYBERPARK SCRAPER =====================

def get_cyberpark_jobs():
    driver = get_driver()
    driver.get("https://www.ulcyberpark.com/jobs")
    time.sleep(6)

    jobs = []

    cards = driver.find_elements(By.CSS_SELECTOR, "div.job-listing")

    for card in cards:
        try:
            title = card.find_element(By.TAG_NAME, "h3").text.strip()
            link  = card.find_element(By.TAG_NAME, "a").get_attribute("href")

            jobs.append({
                "title": title,
                "company": "Cyberpark",
                "link": link
            })
        except:
            continue

    driver.quit()
    return jobs

# ===================== EMAIL =====================

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    body = ""

    if not jobs:
        body = "No jobs found today."
    else:
        for j in jobs:
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

# ===================== MAIN =====================

if __name__ == "__main__":
    jobs = get_cyberpark_jobs()
    print("Jobs scraped:", len(jobs))

    for j in jobs:
        print(j)

    send_email(jobs)
