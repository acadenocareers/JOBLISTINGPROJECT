import os
import time
import smtplib
import random
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========== QUOTES ==========
QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications.",
    "Opportunities don’t happen, you create them.",
    "Small steps today lead to big success tomorrow."
]

# ========== EMAIL CONFIG ==========
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO").split(",")
STUDENT_NAMES = os.getenv("STUDENT_NAMES").split(",")
TRACKER_URL = os.getenv("TRACKER_URL")

# ========== SCRAPER SETUP ==========
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ========== SCRAPE JOBS ==========
def scrape_jobs():
    jobs = []
    driver.get("https://www.indeed.com/jobs?q=python&l=India")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    for card in soup.select(".result"):
        title = card.select_one("h2")
        company = card.select_one(".companyName")
        link = card.select_one("a")

        if title and company and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "link": "https://www.indeed.com" + link.get("href")
            })
    return jobs

# ========== EMAIL SENDER ==========
def send_email(jobs):
    quote = random.choice(QUOTES)
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"

    for i, email in enumerate(EMAIL_TO):
        name = STUDENT_NAMES[i] if i < len(STUDENT_NAMES) else "Student"

        html = f"""
        <h2>Hello {name},</h2>
        <p><b>{quote}</b></p>
        <hr>
        """

        for job in jobs:
            tracking = f"{TRACKER_URL}?name={name}&email={email}&job={urllib.parse.quote(job['title'])}&link={urllib.parse.quote(job['link'])}"

            html += f"""
            <div style='margin-bottom:15px'>
                <b>{job['title']}</b><br>
                {job['company']}<br>
                <a href="{tracking}" style='background:#6a00ff;color:white;padding:8px 12px;border-radius:6px;text-decoration:none'>Apply</a>
            </div>
            """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        print(f"Email sent to {name}")

# ========== MAIN ==========
if __name__ == "__main__":
    jobs = scrape_jobs()
    df = pd.DataFrame(jobs)
    df.to_csv("jobs.csv", index=False)

    if jobs:
        send_email(jobs)
    driver.quit()
