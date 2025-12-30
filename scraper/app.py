import requests
from bs4 import BeautifulSoup
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText

# =========================
# EMAIL CONFIG
# =========================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# SCRAPERS
# =========================
def scrape_technopark():
    url = "https://www.technopark.org/job-search"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    jobs = []
    for job in soup.select(".job-listing"):
        title = job.select_one("h3").text.strip()
        company = job.select_one(".company").text.strip()
        location = "Technopark, Trivandrum"
        link = job.find("a")["href"]

        jobs.append(f"{title} | {company} | {location}\n{link}")

    return jobs

def scrape_infopark():
    url = "https://infopark.in/companies/job"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    jobs = []
    for job in soup.select(".job-list"):
        title = job.select_one("h4").text.strip()
        company = job.select_one(".company-name").text.strip()
        location = "Infopark, Kochi"
        link = "https://infopark.in" + job.find("a")["href"]

        jobs.append(f"{title} | {company} | {location}\n{link}")

    return jobs

def scrape_cyberpark():
    url = "https://www.cyberparkkerala.org/jobs"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    jobs = []
    for job in soup.select(".job-block"):
        title = job.select_one("h5").text.strip()
        company = job.select_one(".company-name").text.strip()
        location = "Cyberpark, Kozhikode"
        link = job.find("a")["href"]

        jobs.append(f"{title} | {company} | {location}\n{link}")

    return jobs

# =========================
# EMAIL
# =========================
def send_email(all_jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    if not all_jobs:
        body = "No jobs found today."
    else:
        body = "\n\n".join(all_jobs)

    msg = MIMEText(body)
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Mail sent successfully")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🚀 Starting Kerala IT Job Scraper...")

    jobs = []
    jobs += scrape_technopark()
    jobs += scrape_infopark()
    jobs += scrape_cyberpark()

    print(f"✅ Total jobs collected: {len(jobs)}")
    send_email(jobs)
